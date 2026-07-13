from app.database import get_connection

with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user;")
        database_name, user_name = cursor.fetchone()

print(f"База: {database_name}")
print(f"Пользователь: {user_name}")
