import logging
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from validate_leads import load_and_validate

PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "leads.csv"
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "load_leads.log"

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

load_dotenv(ENV_FILE)

connection_settings = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}


def get_required_id(cursor, query: str, value: str, entity_name: str) -> int:
    cursor.execute(query, (value,))
    result = cursor.fetchone()

    if result is None:
        raise ValueError(f"Не найден {entity_name}: {value}")

    return result[0]


def main() -> None:
    leads = load_and_validate(INPUT_FILE)

    inserted_count = 0
    skipped_count = 0

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            for lead in leads.itertuples(index=False):
                customer_phone = lead.customer_phone.strip()
                manager_email = lead.manager_email.strip()
                source_name = lead.source.strip()
                service_name = lead.service_name.strip()
                desired_date = lead.desired_date.strip()

                customer_id = get_required_id(
                    cursor,
                    "SELECT id FROM customers WHERE phone = %s",
                    customer_phone,
                    "клиент с телефоном",
                )
                manager_id = get_required_id(
                    cursor,
                    "SELECT id FROM managers WHERE email = %s",
                    manager_email,
                    "менеджер с email",
                )
                source_id = get_required_id(
                    cursor,
                    "SELECT id FROM advertising_sources WHERE name = %s",
                    source_name,
                    "источник",
                )

                cursor.execute(
                    """
                    SELECT id
                    FROM leads
                    WHERE customer_id = %s
                      AND service_name = %s
                      AND desired_date = %s
                    """,
                    (customer_id, service_name, desired_date),
                )
                existing_lead = cursor.fetchone()

                if existing_lead:
                    skipped_count += 1
                    continue

                cursor.execute(
                    """
                    INSERT INTO leads (
                        customer_id,
                        manager_id,
                        advertising_source_id,
                        service_name,
                        status,
                        desired_date,
                        comment
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        customer_id,
                        manager_id,
                        source_id,
                        service_name,
                        lead.status.strip(),
                        desired_date,
                        lead.comment.strip() or None,
                    ),
                )
                inserted_count += 1

    logger.info(
        "Загрузка заявок завершена. Добавлено: %s. Пропущено: %s.",
        inserted_count,
        skipped_count,
    )
    print(f"Добавлено заявок: {inserted_count}")
    print(f"Пропущено существующих заявок: {skipped_count}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Ошибка при загрузке заявок.")
        raise
