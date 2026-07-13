CREATE TABLE IF NOT EXISTS leads (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    service VARCHAR(50) NOT NULL,
    district VARCHAR(200) NOT NULL,
    desired_date DATE,
    comment TEXT,
    consent BOOLEAN NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    crm_external_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads (phone);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads (created_at);
