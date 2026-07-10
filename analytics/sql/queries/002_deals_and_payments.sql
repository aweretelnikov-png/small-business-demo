SELECT
       deals.id AS deal_id,
       deals.amount AS deal_amount,
       deals.status AS deal_status,
       COALESCE(SUM(payments.amount), 0) AS paid_amount
   FROM deals
   LEFT JOIN payments ON payments.deal_id = deals.id
   GROUP BY deals.id, deals.amount, deals.status
   ORDER BY deals.id;