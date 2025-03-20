from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'etl_analytics_sessions',
    default_args=default_args,
    description='ETL pipeline to aggregate user sessions data',
    schedule_interval='*/10 * * * *',
    start_date=datetime(2025, 3, 19),
    catchup=False,
)

def extract_data_from_projects(**kwargs):
    """
    Extract data from project databases.
    """
    project_connections = ['project_a_conn', 'project_b_conn', 'project_c_conn']
    all_sessions = []

    for conn_id in project_connections:
        hook = PostgresHook(postgres_conn_id=conn_id)
        query = """
            SELECT
                us.id AS session_id,
                us.user_id,
                us.page_name,
                COUNT(e.id) AS events_count,
                us.created_at AS session_date
            FROM user_sessions us
            LEFT JOIN events e ON us.id = e.user_id
            GROUP BY us.id, us.user_id, us.page_name, us.created_at
        """
        sessions = hook.get_pandas_df(query)
        sessions['project'] = conn_id.split('_')[1]
        all_sessions.append(sessions)

    # Combine data from all projects
    combined_sessions = pd.concat(all_sessions, ignore_index=True)

    combined_sessions['session_date'] = combined_sessions['session_date'].astype(str)

    return combined_sessions.to_dict('records')

def enrich_data_with_transactions(**kwargs):
    """
    Enrich data.
    - Sum of successful transactions for each session.
    - First successful transaction on the session date.
    """
    ti = kwargs['ti']
    sessions = pd.DataFrame(ti.xcom_pull(task_ids='extract_data_from_projects'))

    analytics_hook = PostgresHook(postgres_conn_id='analytics_conn')

    transactions_query = """
        SELECT id, user_id, created_at, amount, currency, success
        FROM transactions
        WHERE success = TRUE
    """
    exchange_rates_query = """
        SELECT currency_from, currency_to, exchange_rate, currency_date
        FROM exchange_rates
    """
    transactions = analytics_hook.get_pandas_df(transactions_query)
    exchange_rates = analytics_hook.get_pandas_df(exchange_rates_query)

    transactions['created_at'] = pd.to_datetime(transactions['created_at'])
    exchange_rates['currency_date'] = pd.to_datetime(exchange_rates['currency_date'])

    sessions['transactions_sum'] = 0
    sessions['first_successful_transaction_time'] = None
    sessions['first_successful_transaction_usd'] = 0

    # Сalculate metrics
    for index, session in sessions.iterrows():
        user_transactions = transactions[
            (transactions['user_id'] == session['user_id']) &
            (transactions['created_at'].dt.date == pd.to_datetime(session['session_date']).date())
        ]

        if not user_transactions.empty:
            user_transactions = user_transactions.merge(
                exchange_rates,
                left_on=['currency', 'created_at'],
                right_on=['currency_from', 'currency_date'],
                how='left'
            )
            user_transactions['amount_usd'] = user_transactions['amount'] * user_transactions['exchange_rate']

            sessions.at[index, 'transactions_sum'] = user_transactions['amount_usd'].sum()

            first_transaction = user_transactions.sort_values('created_at').iloc[0]
            sessions.at[index, 'first_successful_transaction_time'] = first_transaction['created_at']
            sessions.at[index, 'first_successful_transaction_usd'] = first_transaction['amount_usd']

    # XCom compatibility
    sessions['first_successful_transaction_time'] = sessions['first_successful_transaction_time'].astype(str)

    return sessions.to_dict('records')

def load_data_to_analytics(**kwargs):
    """
    Load enriched data into the analytics_sessions table.
    """
    ti = kwargs['ti']
    enriched_sessions = pd.DataFrame(ti.xcom_pull(task_ids='enrich_data_with_transactions'))

    analytics_hook = PostgresHook(postgres_conn_id='analytics_conn')

    for _, row in enriched_sessions.iterrows():
        insert_query = """
            INSERT INTO analytics_sessions (
                session_id, user_id, project, page_name, events_count,
                transactions_sum, first_successful_transaction_time,
                first_successful_transaction_usd, session_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO NOTHING
        """
        parameters = (
            row['session_id'],
            row['user_id'],
            row['project'],
            row['page_name'],
            row['events_count'],
            row['transactions_sum'],
            row['first_successful_transaction_time'] if row['first_successful_transaction_time'] != 'None' else None,
            row['first_successful_transaction_usd'],
            row['session_date']
        )
        analytics_hook.run(insert_query, parameters=parameters)

extract_task = PythonOperator(
    task_id='extract_data_from_projects',
    python_callable=extract_data_from_projects,
    provide_context=True,
    dag=dag,
)

enrich_task = PythonOperator(
    task_id='enrich_data_with_transactions',
    python_callable=enrich_data_with_transactions,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data_to_analytics',
    python_callable=load_data_to_analytics,
    provide_context=True,
    dag=dag,
)

extract_task >> enrich_task >> load_task