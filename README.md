# Small Business Demo — «Фальшивые двери»

Учебный демонстрационный стенд для небольшой компании, устанавливающей фальшивые и скрытые двери в Москве и Московской области.

## Цель проекта

Построить связку для малого бизнеса:

```text
Документы → AI FAQ
Данные продаж → PostgreSQL → Metabase
Сайт → FastAPI → CRM → уведомления
```

Все три учебных модуля реализованы: аналитика, AI FAQ и полный CRM-контур заявок.

## Готово: аналитика продаж

Модуль [`analytics/`](analytics/) уже позволяет:

- запустить PostgreSQL и Metabase в Docker;
- загрузить клиентов из CSV или Excel через Python;
- загрузить заявки, сделки и оплаты из CSV;
- проверить структуру и качество входных данных;
- предотвратить дубли при повторном запуске;
- построить дашборды в Metabase;
- сделать backup PostgreSQL.

### Архитектура

```text
CSV / XLSX
    ↓
Python ETL
    ↓
PostgreSQL (Docker)
    ↓
Metabase (Docker)
    ↓
Дашборды и отчёты
```

### Стек

- Docker Compose
- PostgreSQL 16
- Python 3.12
- pandas, openpyxl, psycopg
- DBeaver
- Metabase
- Git и GitHub

### Основные показатели

- количество заявок;
- фактическая выручка;
- средний чек;
- конверсия заявок в продажи;
- воронка заявок;
- работа менеджеров;
- эффективность рекламных источников;
- сделки без полной оплаты.

## Дашборды

### Панель владельца

![Панель владельца](docs/screenshots/owner-dashboard.png)

### Воронка продаж

![Воронка продаж](docs/screenshots/sales-funnel.png)

### Работа менеджеров

![Работа менеджеров](docs/screenshots/manager-performance.png)

### Источники клиентов

![Источники клиентов](docs/screenshots/marketing-sources.png)

## Быстрый запуск аналитики

```cmd
cd analytics
docker compose up -d
```

После запуска:

- Metabase: <http://localhost:3000>
- PostgreSQL для DBeaver: `localhost:5432`

Подробная инструкция: [`analytics/README.md`](analytics/README.md).

## Обновление данных

```cmd
cd analytics
.venv\Scripts\activate
python etl\run_all.py
```

## Готово: AI FAQ

Модуль [`ai-faq/`](ai-faq/) включает:

- Open WebUI в Docker;
- клиентскую базу знаний;
- отдельную внутреннюю базу сотрудников;
- локальные и облачные модели через Ollama;
- строгий RAG Template;
- многоязычные embeddings и гибридный поиск;
- 50 клиентских тестов;
- переиспользуемый API-автотестер;
- backup Open WebUI с проверкой восстановления.

### Архитектура AI FAQ

```text
Markdown-документы
    ↓
retrieval / embeddings
    ↓
LLM через Ollama Cloud
    ↓
ответ по базе знаний
```

### Клиентский ассистент

![Клиентский AI FAQ](docs/screenshots/ai-faq-client.png)

### Внутренний помощник сотрудников

![Внутренний помощник](docs/screenshots/ai-faq-internal.png)

### Раздельные базы знаний

![Базы знаний AI FAQ](docs/screenshots/ai-faq-knowledge.png)

Подробная инструкция: [`ai-faq/README.md`](ai-faq/README.md).

## Готово: CRM и заявки

Модуль [`crm-leads/`](crm-leads/) включает:

- форму заявки и FastAPI;
- PostgreSQL `crm_demo`;
- Telegram-уведомления;
- создание контактов и сделок Twenty CRM;
- защиту от дублей и повторную синхронизацию;
- подписанный webhook этапов воронки;
- историю статусов;
- CRM-дашборд Metabase без персональных данных;
- автоматические backend-тесты;
- полный backup и изолированные restore-тесты.

### Архитектура CRM

```text
Сайт → FastAPI → PostgreSQL
                  ├→ Telegram
                  ├→ Twenty CRM
                  └→ Metabase

Twenty Stage → signed webhook → FastAPI → история → Metabase
```

Подробная инструкция: [`crm-leads/README.md`](crm-leads/README.md).

## Структура проекта

```text
small-business-demo/
├── analytics/       # PostgreSQL, Metabase и ETL
├── ai-faq/          # Open WebUI, базы знаний и автотесты
├── crm-leads/       # сайт, FastAPI, Telegram, Twenty CRM и Metabase
├── shared/          # общие компоненты
└── docs/            # документация проекта
```

## План развития

- [x] Аналитика продаж: PostgreSQL, Metabase, CSV/XLSX ETL
- [x] AI FAQ: клиентская/внутренняя базы, RAG и 50 тестов
- [x] CRM и заявки: сайт, FastAPI, Telegram, Twenty CRM и Metabase

## Демо-данные и безопасность

Репозиторий содержит только вымышленные демонстрационные данные. Локальные пароли, `.env`, логи и backup-файлы исключены из Git.
