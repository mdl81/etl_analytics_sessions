CREATE TABLE user_sessions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    active BOOLEAN NOT NULL,
    page_name TEXT NOT NULL,
    last_activity_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE pages (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE events (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_name TEXT NOT NULL,
    page_id BIGINT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_page FOREIGN KEY (page_id) REFERENCES pages (id) ON DELETE CASCADE
);


COPY user_sessions(id, user_id, active, page_name, last_activity_at, created_at, updated_at)
FROM '/docker-entrypoint-initdb.d/project_b_user_sessions.csv'
DELIMITER ','
CSV HEADER;

COPY pages(id, name, created_at)
FROM '/docker-entrypoint-initdb.d/project_b_pages.csv'
DELIMITER ','
CSV HEADER;

COPY events(id, user_id, event_name, page_id, created_at)
FROM '/docker-entrypoint-initdb.d/project_b_events.csv'
DELIMITER ','
CSV HEADER;