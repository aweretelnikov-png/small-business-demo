 CREATE OR REPLACE VIEW view_manager_performance AS
   SELECT
       managers.id AS manager_id,
       managers.full_name AS manager,
       COUNT(DISTINCT leads.id) AS leads_count,
       COUNT(
           DISTINCT CASE
               WHEN deals.status = 'won' THEN deals.id
           END
       ) AS won_deals_count,
       COALESCE(SUM(payments.amount), 0) AS revenue
   FROM managers
   LEFT JOIN leads ON leads.manager_id = managers.id
   LEFT JOIN deals ON deals.lead_id = leads.id
   LEFT JOIN payments ON payments.deal_id = deals.id
   GROUP BY managers.id, managers.full_name;