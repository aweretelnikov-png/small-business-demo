import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from validate_customers import load_and_validate

PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "customers.csv"

load_dotenv(ENV_FILE)

connection_settings = {
       "host": os.environ["DB_HOST"],
       "port": os.environ["DB_PORT"],
       "dbname": os.environ["DB_NAME"],
       "user": os.environ["DB_USER"],
       "password": os.environ["DB_PASSWORD"],
}

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

print(f"Добавлено клиентов: {inserted_count}")
print(f"Пропущено существующих клиентов: {skipped_count}")