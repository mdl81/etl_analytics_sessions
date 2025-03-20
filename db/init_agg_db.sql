CREATE TABLE transactions (
    project TEXT NOT NULL, 
    id BIGINT PRIMARY KEY, 
    user_id BIGINT NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    amount NUMERIC NOT NULL, 
    currency TEXT NOT NULL, 
    success BOOLEAN NOT NULL 
);

CREATE TABLE exchange_rates (
    currency_from TEXT NOT NULL, 
    currency_to TEXT NOT NULL, 
    exchange_rate NUMERIC NOT NULL, 
    currency_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (currency_from, currency_to, currency_date) 
);

CREATE TABLE analytics_sessions (
    session_id BIGINT PRIMARY KEY, 
    user_id BIGINT NOT NULL, 
    project TEXT NOT NULL, 
    page_name TEXT NOT NULL, 
    events_count INT NOT NULL, 
    transactions_sum NUMERIC, 
    first_successful_transaction_time TIMESTAMP, 
    first_successful_transaction_usd NUMERIC, 
    session_date DATE NOT NULL 
);


COPY transactions(project, id, user_id, created_at, amount, currency, success)
FROM '/docker-entrypoint-initdb.d/transactions.csv'
DELIMITER ','
CSV HEADER;

COPY exchange_rates(currency_from, currency_to, exchange_rate, currency_date)
FROM '/docker-entrypoint-initdb.d/exchange_rates.csv'
DELIMITER ','
CSV HEADER;