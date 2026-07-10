SELECT
       leads.id AS lead_id,
       customers.full_name AS customer,
       managers.full_name AS manager,
       advertising_sources.name AS source,
       leads.service_name,
       leads.status,
       leads.desired_date
   FROM leads
   JOIN customers ON customers.id = leads.customer_id
   LEFT JOIN managers ON managers.id = leads.manager_id
   LEFT JOIN advertising_sources
       ON advertising_sources.id = leads.advertising_source_id;