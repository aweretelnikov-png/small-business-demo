CREATE TABLE IF NOT EXISTS deals (
       id BIGSERIAL PRIMARY KEY,
       lead_id BIGINT NOT NULL REFERENCES leads(id),
       manager_id BIGINT REFERENCES managers(id),
       amount NUMERIC(12, 2),
       status VARCHAR(50) NOT NULL DEFAULT 'proposal',
       closed_at TIMESTAMPTZ,
       created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );