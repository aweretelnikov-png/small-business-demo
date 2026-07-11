 CREATE OR REPLACE VIEW view_sales_funnel AS
   SELECT
       status,
       COUNT(*) AS leads_count
   FROM leads
   GROUP BY status;