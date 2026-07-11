CREATE OR REPLACE VIEW view_sales_summary AS
   WITH paid_deals AS (
       SELECT
           deals.id,
           SUM(payments.amount) AS paid_amount
       FROM deals
       JOIN payments ON payments.deal_id = deals.id
       WHERE deals.status = 'won'
       GROUP BY deals.id
   )
   SELECT
       (SELECT COUNT(*) FROM leads) AS total_leads,
       (SELECT COUNT(*) FROM deals WHERE status = 'won') AS won_deals,
       (SELECT COALESCE(SUM(amount), 0) FROM payments) AS revenue,
       (
           SELECT COALESCE(ROUND(AVG(paid_amount), 2), 0)
           FROM paid_deals
       ) AS average_check;