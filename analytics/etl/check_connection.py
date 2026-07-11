import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)

connection_settings = {
       "host": os.environ["DB_HOST"],
       "port": os.environ["DB_PORT"],
       "dbname": os.environ["DB_NAME"],
       "user": os.environ["DB_USER"],
       "password": os.environ["DB_PASSWORD"],
}

with psycopg.connect(**connection_settings) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
               "SELECT current_database(), current_user, version();"
        )
        database_name, user_name, version = cursor.fetchone()

print(f"База: {database_name}")
print(f"Пользователь: {user_name}")
print(f"PostgreSQL: {version}")