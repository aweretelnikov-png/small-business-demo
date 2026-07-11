CREATE OR REPLACE VIEW view_marketing_sources AS
   SELECT
       COALESCE(advertising_sources.name, 'Не указан') AS source,
       COUNT(DISTINCT leads.id) AS leads_count,
       COUNT(
           DISTINCT CASE
               WHEN deals.status = 'won' THEN deals.id
           END
       ) AS won_deals_count,
       COALESCE(SUM(payments.amount), 0) AS revenue,
       ROUND(
           100.0 * COUNT(
               DISTINCT CASE
                   WHEN deals.status = 'won' THEN leads.id
               END
           ) / NULLIF(COUNT(DISTINCT leads.id), 0),
           1
       ) AS conversion_percent
   FROM leads
   LEFT JOIN advertising_sources
       ON advertising_sources.id = leads.advertising_source_id
   LEFT JOIN deals ON deals.lead_id = leads.id
   LEFT JOIN payments ON payments.deal_id = deals.id
   GROUP BY advertising_sources.name;