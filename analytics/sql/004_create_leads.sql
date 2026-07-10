CREATE TABLE IF NOT EXISTS leads (
       id BIGSERIAL PRIMARY KEY,
       customer_id BIGINT NOT NULL REFERENCES customers(id),
       manager_id BIGINT REFERENCES managers(id),
       advertising_source_id BIGINT REFERENCES advertising_sources(id),
       service_name VARCHAR(200) NOT NULL,
       status VARCHAR(50) NOT NULL DEFAULT 'new',
       desired_date DATE,
       comment TEXT,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );