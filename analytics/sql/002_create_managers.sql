CREATE TABLE IF NOT EXISTS managers (
       id BIGSERIAL PRIMARY KEY,
       full_name VARCHAR(200) NOT NULL,
       email VARCHAR(255) UNIQUE,
       phone VARCHAR(30),
       hired_at DATE,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );