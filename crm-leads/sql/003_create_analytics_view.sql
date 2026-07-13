CREATE OR REPLACE VIEW v_crm_leads AS
SELECT
    id AS lead_id,
    created_at,
    created_at::date AS created_date,
    service AS service_code,
    CASE service
        WHEN 'false-door' THEN 'Фальшивая дверь'
        WHEN 'hidden-door' THEN 'Скрытая дверь'
        WHEN 'decorative-door' THEN 'Декоративная дверь'
        ELSE service
    END AS service_name,
    district,
    desired_date,
    status AS lead_status,
    crm_sync_status,
    crm_synced_at,
    CASE
        WHEN crm_synced_at IS NOT NULL
        THEN ROUND(EXTRACT(EPOCH FROM (crm_synced_at - created_at))::numeric, 2)
    END AS crm_sync_seconds,
    (comment IS NOT NULL AND BTRIM(comment) <> '') AS has_comment,
    'website'::text AS lead_source
FROM leads;

COMMENT ON VIEW v_crm_leads IS
    'Обезличенное представление заявок для Metabase';
