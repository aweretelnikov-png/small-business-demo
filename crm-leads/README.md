# CRM и заявки — «Фальшивые двери»

Учебный end-to-end проект обработки заявок малого бизнеса.

## Архитектура

```text
Сайт :5500
   ↓ POST /api/leads
FastAPI :8000
   ↓
PostgreSQL crm_demo :5433
   ├─ background → Telegram
   ├─ background → Twenty CRM :3002
   └─ Metabase :3000

Twenty Stage
   ↓ signed webhook
FastAPI → crm_demo → Metabase
```

## Возможности

- frontend-форма заявки;
- серверная Pydantic-валидация;
- нормализация российского телефона;
- сохранение в PostgreSQL;
- Telegram-уведомление;
- создание/повторное использование контакта Twenty;
- создание сделки Twenty без дублей;
- фоновая обработка интеграций;
- подписанный webhook статусов Twenty;
- история движения по воронке;
- обезличенные VIEW для Metabase;
- полный backup и изолированные restore-тесты;
- автоматические backend-тесты.

## Порты

| Сервис | URL / порт |
|---|---|
| Frontend | <http://localhost:5500> |
| FastAPI | <http://localhost:8000> |
| Swagger | <http://localhost:8000/docs> |
| crm_demo для DBeaver | `127.0.0.1:5433` |
| Metabase | <http://localhost:3000> |
| Twenty | <http://localhost:3002> |

## Настройки

Создайте локальные файлы по шаблонам:

```text
crm-leads/.env.example         → crm-leads/.env
backend/.env.example           → backend/.env
twenty/.env.example            → twenty/.env
```

Все `.env` игнорируются Git. Не публикуйте пароли, API-ключи, Telegram-токены, webhook secret и `ENCRYPTION_KEY` Twenty.

Для Windows/Hiddify в backend используется:

```env
DB_HOST=127.0.0.1
```

## Запуск инфраструктуры

Общая сеть создаётся один раз:

```cmd
docker network create small-business-demo-network
```

CRM PostgreSQL:

```cmd
cd crm-leads
docker compose up -d
```

Twenty:

```cmd
cd twenty
docker compose up -d
```

Metabase и аналитическая база:

```cmd
cd ..\..\analytics
docker compose up -d
```

## Backend

```cmd
cd crm-leads\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`0.0.0.0` нужен локальному webhook Twenty через `host.docker.internal`. В Windows Firewall разрешайте только частные сети.

## Frontend

Из `crm-leads`:

```cmd
python -m http.server 5500 --directory frontend
```

Откройте <http://localhost:5500>.

## Миграции

Выполняются последовательно в `crm_demo`:

```text
sql/001_create_leads.sql
sql/002_add_crm_sync_status.sql
sql/003_create_analytics_view.sql
sql/004_create_lead_status_history.sql
sql/005_add_funnel_analytics_views.sql
```

## Проверки интеграций

Из `backend` с активным `.venv`:

```cmd
python check_database.py
python check_telegram.py
python check_twenty.py
python sync_pending_leads.py
```

`sync_pending_leads.py` повторяет `pending` и `failed` синхронизации. Внешний ID защищает Twenty от дублей.

## Тесты

```cmd
python -m pytest -v
```

Текущий набор проверяет схемы, API, фоновые интеграции, ошибки Telegram/Twenty, HMAC и форматы webhook.

## Twenty webhook

URL локального webhook:

```text
http://host.docker.internal:8000/api/webhooks/twenty
```

Фильтр: `Opportunity → Updated`. Secret должен совпадать с `TWENTY_WEBHOOK_SECRET`.

Для локального стенда у worker отключён outbound safe mode, чтобы разрешить private IP. В production его следует включить и использовать публичный HTTPS endpoint или безопасный шлюз.

## Metabase

Metabase подключается к CRM через Docker-сеть:

```text
Host: crm-postgres
Port: 5432
Database: crm_demo
```

Для аналитики используются обезличенные VIEW:

- `v_crm_leads`;
- `v_lead_status_history`.

## Backup и restore

См. [BACKUP_RESTORE.md](BACKUP_RESTORE.md).

Создание полного backup:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\backup.ps1
```

Backup содержит персональные данные и игнорируется Git. `.env` храните отдельно в защищённом хранилище.

## Ограничения текущей версии

Перед публичным production-развёртыванием нужны:

- HTTPS и reverse proxy;
- авторизация `GET /api/leads`;
- rate limiting и anti-spam;
- внешняя очередь задач вместо FastAPI `BackgroundTasks`;
- ограниченные роли API-ключей;
- централизованные логи и мониторинг;
- регулярные автоматические backup и restore-тесты;
- политика хранения и удаления персональных данных;
- закреплённые версии Docker images вместо `latest`.
