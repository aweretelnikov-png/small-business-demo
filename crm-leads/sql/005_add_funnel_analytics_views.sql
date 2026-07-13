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
    'website'::text AS lead_source,
    status_updated_at,
    CASE status
        WHEN 'new' THEN 'Новая заявка'
        WHEN 'contacted' THEN 'Связались'
        WHEN 'measurement_scheduled' THEN 'Назначен замер'
        WHEN 'proposal_sent' THEN 'Предложение отправлено'
        WHEN 'awaiting_payment' THEN 'Ожидается оплата'
        WHEN 'won' THEN 'Успешно'
        WHEN 'lost' THEN 'Отказ'
        ELSE status
    END AS lead_status_name
FROM leads;

CREATE OR REPLACE VIEW v_lead_status_history AS
SELECT
    history.id AS status_event_id,
    history.lead_id,
    leads.service AS service_code,
    CASE leads.service
        WHEN 'false-door' THEN 'Фальшивая дверь'
        WHEN 'hidden-door' THEN 'Скрытая дверь'
        WHEN 'decorative-door' THEN 'Декоративная дверь'
        ELSE leads.service
    END AS service_name,
    history.old_status,
    history.new_status,
    CASE history.new_status
        WHEN 'new' THEN 'Новая заявка'
        WHEN 'contacted' THEN 'Связались'
        WHEN 'measurement_scheduled' THEN 'Назначен замер'
        WHEN 'proposal_sent' THEN 'Предложение отправлено'
        WHEN 'awaiting_payment' THEN 'Ожидается оплата'
        WHEN 'won' THEN 'Успешно'
        WHEN 'lost' THEN 'Отказ'
        ELSE history.new_status
    END AS new_status_name,
    history.source,
    history.changed_at,
    history.changed_at::date AS changed_date,
    ROUND(
        EXTRACT(
            EPOCH FROM (
                history.changed_at
                - LAG(history.changed_at) OVER (
                    PARTITION BY history.lead_id
                    ORDER BY history.changed_at
                )
            )
        )::numeric,
        2
    ) AS seconds_since_previous_status
FROM lead_status_history AS history
JOIN leads ON leads.id = history.lead_id;

COMMENT ON VIEW v_lead_status_history IS
    'Обезличенная история переходов заявок для анализа воронки';
