ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS status_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

UPDATE leads
SET status_updated_at = created_at
WHERE status = 'new';

CREATE TABLE IF NOT EXISTS lead_status_history (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL REFERENCES leads (id) ON DELETE CASCADE,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_lead_status_history_event
        UNIQUE (lead_id, new_status, changed_at)
);

INSERT INTO lead_status_history (
    lead_id,
    old_status,
    new_status,
    source,
    changed_at
)
SELECT
    id,
    NULL,
    status,
    'initial',
    created_at
FROM leads
ON CONFLICT (lead_id, new_status, changed_at) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_lead_status_history_lead_id
    ON lead_status_history (lead_id);

CREATE INDEX IF NOT EXISTS idx_lead_status_history_changed_at
    ON lead_status_history (changed_at);
