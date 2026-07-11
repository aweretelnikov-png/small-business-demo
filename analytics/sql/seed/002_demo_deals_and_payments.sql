 INSERT INTO deals (lead_id, manager_id, amount, status, closed_at)
   SELECT
       leads.id,
       leads.manager_id,
       32000.00,
       'won',
       '2026-06-22 16:00:00+03'
   FROM leads
   JOIN customers ON customers.id = leads.customer_id
   WHERE customers.full_name = 'Кира Павлова';

   INSERT INTO deals (lead_id, manager_id, amount, status, closed_at)
   SELECT
       leads.id,
       leads.manager_id,
       45000.00,
       'proposal',
       NULL
   FROM leads
   JOIN customers ON customers.id = leads.customer_id
   WHERE customers.full_name = 'Ольга Морозова';

   INSERT INTO payments (deal_id, amount, paid_at, payment_method)
   SELECT
       deals.id,
       32000.00,
       '2026-06-22 16:30:00+03',
       'Банковский перевод'
   FROM deals
   JOIN leads ON leads.id = deals.lead_id
   JOIN customers ON customers.id = leads.customer_id
   WHERE customers.full_name = 'Кира Павлова'
     AND deals.status = 'won';