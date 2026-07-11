# Small Business Demo — «Фальшивые двери»

Учебный демонстрационный стенд для небольшой компании, устанавливающей фальшивые и скрытые двери в Москве и Московской области.

## Цель проекта

Построить связку для малого бизнеса:

```text
Источники данных → PostgreSQL → Metabase → бизнес-аналитика
```

В следующих модулях проект будет расширен AI FAQ, формой заявок, FastAPI, Telegram и Twenty CRM.

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

## Структура проекта

```text
small-business-demo/
├── analytics/       # PostgreSQL, Metabase и ETL
├── ai-faq/          # будущий модуль AI FAQ
├── crm-leads/       # будущие сайт, FastAPI и CRM
├── shared/          # общие компоненты
└── docs/            # документация проекта
```

## План развития

- [x] Аналитика продаж: PostgreSQL, Metabase, CSV/XLSX ETL
- [ ] AI FAQ: Open WebUI и база знаний компании
- [ ] CRM и заявки: сайт, FastAPI, Telegram, Twenty CRM

## Демо-данные и безопасность

Репозиторий содержит только вымышленные демонстрационные данные. Локальные пароли, `.env`, логи и backup-файлы исключены из Git.
