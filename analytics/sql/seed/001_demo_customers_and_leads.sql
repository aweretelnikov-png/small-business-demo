INSERT INTO customers (full_name, phone, email)
   VALUES
       ('Сергей Иванов', '+7 999 456-78-90', 'sergey@example.com'),
       ('Ольга Морозова', '+7 999 567-89-01', 'olga@example.com'),
       ('Дмитрий Соколов', '+7 999 678-90-12', 'dmitry@example.com'),
       ('Кира Павлова', '+7 999 789-01-23', 'kira@example.com');

   INSERT INTO advertising_sources (name)
   VALUES
       ('Авито'),
       ('VK Реклама')
   ON CONFLICT (name) DO NOTHING;

   INSERT INTO leads (
       customer_id,
       manager_id,
       advertising_source_id,
       service_name,
       status,
       desired_date,
       comment
   )
   VALUES
   (
       (SELECT id FROM customers WHERE full_name = 'Сергей Иванов'),
       (SELECT id FROM managers WHERE full_name = 'Алексей Орлов'),
       (SELECT id FROM advertising_sources WHERE name = 'Telegram'),
       'Установка скрытой двери',
       'contacted',
       '2026-07-21',
       'Нужна консультация по материалам'
   ),
   (
       (SELECT id FROM customers WHERE full_name = 'Ольга Морозова'),
       (SELECT id FROM managers WHERE full_name = 'Елена Волкова'),
       (SELECT id FROM advertising_sources WHERE name = 'Авито'),
       'Монтаж декоративной двери',
       'proposal',
       '2026-07-24',
       'Подготовлен предварительный расчёт'
   ),
   (
       (SELECT id FROM customers WHERE full_name = 'Дмитрий Соколов'),
       (SELECT id FROM managers WHERE full_name = 'Алексей Орлов'),
       (SELECT id FROM advertising_sources WHERE name = 'VK Реклама'),
       'Установка фальшивой двери',
       'new',
       '2026-07-28',
       'Заявка с сайта-партнёра'
   ),
   (
       (SELECT id FROM customers WHERE full_name = 'Кира Павлова'),
       (SELECT id FROM managers WHERE full_name = 'Елена Волкова'),
       (SELECT id FROM advertising_sources WHERE name = 'Сайт'),
       'Установка скрытой двери',
       'closed',
       '2026-06-20',
       'Работы завершены'
   );