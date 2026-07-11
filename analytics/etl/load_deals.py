import logging
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from normalizers import normalize_phone
from validate_deals import load_and_validate

PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "deals.csv"
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "load_deals.log"

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
    deals = load_and_validate(INPUT_FILE)

    inserted_deals = 0
    skipped_deals = 0
    inserted_payments = 0
    skipped_payments = 0

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            for deal in deals.itertuples(index=False):
                customer_phone = normalize_phone(deal.customer_phone)
                manager_email = deal.manager_email.strip()
                service_name = deal.service_name.strip()

                customer_id = get_required_id(
                    cursor,
                    """
                    SELECT id
                    FROM customers
                    WHERE regexp_replace(phone, '\\D', '', 'g') = %s
                    """,
                    customer_phone.removeprefix("+"),
                    "клиент с телефоном",
                )
                manager_id = get_required_id(
                    cursor,
                    "SELECT id FROM managers WHERE email = %s",
                    manager_email,
                    "менеджер с email",
                )

                cursor.execute(
                    """
                    SELECT id
                    FROM leads
                    WHERE customer_id = %s
                      AND manager_id = %s
                      AND service_name = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (customer_id, manager_id, service_name),
                )
                lead = cursor.fetchone()

                if lead is None:
                    raise ValueError(
                        "Не найдена заявка для сделки: "
                        f"клиент={customer_phone}, услуга={service_name}"
                    )

                lead_id = lead[0]
                cursor.execute(
                    """
                    SELECT id
                    FROM deals
                    WHERE lead_id = %s AND amount = %s AND status = %s
                    """,
                    (lead_id, deal.amount, deal.status),
                )
                existing_deal = cursor.fetchone()

                if existing_deal:
                    deal_id = existing_deal[0]
                    skipped_deals += 1
                else:
                    cursor.execute(
                        """
                        INSERT INTO deals (lead_id, manager_id, amount, status, closed_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            lead_id,
                            manager_id,
                            deal.amount,
                            deal.status,
                            deal.closed_at.strip() or None,
                        ),
                    )
                    deal_id = cursor.fetchone()[0]
                    inserted_deals += 1

                if not deal.paid_amount.strip():
                    continue

                cursor.execute(
                    """
                    SELECT id
                    FROM payments
                    WHERE deal_id = %s AND amount = %s AND paid_at = %s
                    """,
                    (deal_id, deal.paid_amount, deal.paid_at),
                )
                existing_payment = cursor.fetchone()

                if existing_payment:
                    skipped_payments += 1
                    continue

                cursor.execute(
                    """
                    INSERT INTO payments (deal_id, amount, paid_at, payment_method)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        deal_id,
                        deal.paid_amount,
                        deal.paid_at,
                        deal.payment_method.strip(),
                    ),
                )
                inserted_payments += 1

    logger.info(
        "Загрузка сделок завершена. Сделок добавлено: %s, пропущено: %s. "
        "Оплат добавлено: %s, пропущено: %s.",
        inserted_deals,
        skipped_deals,
        inserted_payments,
        skipped_payments,
    )
    print(f"Добавлено сделок: {inserted_deals}")
    print(f"Пропущено существующих сделок: {skipped_deals}")
    print(f"Добавлено оплат: {inserted_payments}")
    print(f"Пропущено существующих оплат: {skipped_payments}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Ошибка при загрузке сделок.")
        raise
