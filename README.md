# ETL Analytics Sessions Pipeline

This project is an ETL (Extract, Transform, Load) pipeline built using **Apache Airflow**. The pipeline processes user session data from multiple PostgreSQL databases, enriches it with transaction and exchange rate data, and loads the aggregated results into an analytics database.

## Features
- **Extract**: Retrieves session data from multiple project databases (`project_a_db`, `project_b_db`, `project_c_db`).
- **Transform**: Enriches session data with transaction sums and metrics for the first successful transaction.
- **Load**: Inserts the enriched data into the `analytics_sessions` table in the analytics database (`analytics_db`).
- **Scalable**: Designed to handle data from up to 10 projects dynamically.
- **Scheduled Execution**: Runs every 10 minutes using Airflow's scheduling capabilities.

---

## Project Structure
```
project/
├── dags/
│   └── etl_analytics_sessions.py          # Airflow DAG definition
├── db/
│   ├── init_a_db.sql                      # Initialization script for project_a_db
│   ├── init_b_db.sql                      # Initialization script for project_b_db
│   ├── init_c_db.sql                      # Initialization script for project_c_db
│   └── init_agg_db.sql                    # Initialization script for analytics_db
├── data/
│   ├── project_a_events.csv               # Sample events data for project_a_db
│   ├── project_a_pages.csv                # Sample pages data for project_a_db
│   ├── project_a_user_sessions.csv        # Sample user sessions data for project_a_db
│   ├── project_b_events.csv               # Sample events data for project_b_db
│   ├── project_b_pages.csv                # Sample pages data for project_b_db
│   ├── project_b_user_sessions.csv        # Sample user sessions data for project_b_db
│   ├── transactions.csv                   # Sample transactions data for analytics_db
│   └── exchange_rates.csv                 # Sample exchange rates data for analytics_db
├── docker-compose.yaml                    # Docker Compose configuration
├── .env                                   # Environment variables (not included in version control)
└── README.md                              # Project documentation
```

---

## Prerequisites
- **Docker** and **Docker Compose** installed on your machine.
- **Python 3.8+** (optional, if running Airflow locally without Docker).

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a .env file
Create a .env file in the project root directory and add the following variables:

```bash
# PostgreSQL credentials for Project A
PROJECT_A_DB_USER=user_a
PROJECT_A_DB_PASSWORD=password_a
PROJECT_A_DB_NAME=project_a_db

# PostgreSQL credentials for Project B
PROJECT_B_DB_USER=user_b
PROJECT_B_DB_PASSWORD=password_b
PROJECT_B_DB_NAME=project_b_db

# PostgreSQL credentials for Project C
PROJECT_C_DB_USER=user_c
PROJECT_C_DB_PASSWORD=password_c
PROJECT_C_DB_NAME=project_c_db

# PostgreSQL credentials for Analytics DB
ANALYTICS_DB_USER=analytics_user
ANALYTICS_DB_PASSWORD=analytics_password
ANALYTICS_DB_NAME=agg
```

### 3. Start the Services
Run the following command to start all services (PostgreSQL databases, Airflow, Redis, etc.):
   ```bash
   docker-compose up -d
   ```

### 4. Access the Airflow web interface 
Open your browser and go to [http://localhost:8080](http://localhost:8080).
- Default credentials:
   - Username: airflow
   - Password: airflow
- Enable the etl_analytics_sessions DAG and trigger it manually or let it run on its schedule (every 10 minutes).

---

## License
This project is licensed under the MIT License.

---

### How to Use:
1. Copy the entire content above.
2. Paste it into your `README.md` file.
3. Replace `<repository-url>` and `<repository-name>` with your actual repository URL and name.
4. Save the file.

This version is well-formatted, easy to read, and ready for use in your project!