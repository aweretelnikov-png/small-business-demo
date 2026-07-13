ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS crm_sync_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS crm_sync_error TEXT,
    ADD COLUMN IF NOT EXISTS crm_synced_at TIMESTAMPTZ;

ALTER TABLE leads
    DROP CONSTRAINT IF EXISTS leads_crm_sync_status_check;

ALTER TABLE leads
    ADD CONSTRAINT leads_crm_sync_status_check
    CHECK (crm_sync_status IN ('pending', 'synced', 'failed'));

CREATE INDEX IF NOT EXISTS idx_leads_crm_sync_status
    ON leads (crm_sync_status);
