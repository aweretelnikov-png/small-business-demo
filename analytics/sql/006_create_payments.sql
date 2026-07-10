   CREATE TABLE IF NOT EXISTS payments (
       id BIGSERIAL PRIMARY KEY,
       deal_id BIGINT NOT NULL REFERENCES deals(id),
       amount NUMERIC(12, 2) NOT NULL,
       paid_at TIMESTAMPTZ NOT NULL,
       payment_method VARCHAR(50),
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );