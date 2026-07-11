# Аналитика продаж

Учебный модуль аналитики для компании «Фальшивые двери».

## Сервисы

- **PostgreSQL** — хранит клиентов, заявки, сделки и оплаты.
- **Metabase** — создаёт отчёты и дашборды по данным PostgreSQL.
- **Python ETL** — проверяет и загружает CSV/Excel-файлы в PostgreSQL.

## Запуск сервисов

Из папки `analytics`:

```cmd
docker compose up -d
```

## Остановка сервисов

```cmd
docker compose stop
```

## Проверка состояния

```cmd
docker compose ps
```

## Логи PostgreSQL

```cmd
docker compose logs --tail=20 postgres
```

## Адреса

- Metabase: <http://localhost:3000>
- PostgreSQL для DBeaver: `localhost:5432`

## Подготовка Python-окружения

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Загрузка данных

Исходные файлы находятся в `data/raw/`:

- `customers.csv` или `customers.xlsx`;
- `leads.csv`;
- `deals.csv`.

Запуск всей ETL-цепочки:

```cmd
python etl\run_all.py
```

## Backup PostgreSQL

```cmd
mkdir backups
docker compose exec -T postgres pg_dump -U sales_user -d sales_demo > backups\sales_demo_backup.sql
```

Backup сохраняется в `analytics/backups/` и не добавляется в Git.
