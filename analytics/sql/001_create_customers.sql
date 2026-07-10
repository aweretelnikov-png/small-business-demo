CREATE TABLE IF NOT EXISTS customers (
       id BIGSERIAL PRIMARY KEY,
       full_name VARCHAR(200) NOT NULL,
       phone VARCHAR(30) NOT NULL,
       email VARCHAR(255),
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );