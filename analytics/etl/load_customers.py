import logging
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from validate_customers import load_and_validate

PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "customers.csv"
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "load_customers.log"

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

def main() -> None:
    customers = load_and_validate(INPUT_FILE)

    inserted_count = 0
    skipped_count = 0

    with psycopg.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            for customer in customers.itertuples(index=False):
                   phone = customer.phone.strip()

                   cursor.execute(
                       "SELECT id FROM customers WHERE phone = %s",
                       (phone,),
                   )
                   existing_customer = cursor.fetchone()

                   if existing_customer:
                       skipped_count += 1
                       continue

                   cursor.execute(
                       """
                       INSERT INTO customers (full_name, phone, email)
                       VALUES (%s, %s, %s)
                       """,
                       (
                           customer.full_name.strip(),
                           phone,
                           customer.email.strip() or None,
                       ),
                   )
                   inserted_count += 1

    logger.info(
           "Загрузка завершена. Добавлено: %s. Пропущено: %s.",
           inserted_count,
           skipped_count,
       )
    print(f"Добавлено клиентов: {inserted_count}")
    print(f"Пропущено существующих клиентов: {skipped_count}")


if __name__ == "__main__":
    try:
           main()
    except Exception:
        logger.exception("Ошибка при загрузке клиентов.")
        raise