import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

token = os.environ["TELEGRAM_BOT_TOKEN"]

with httpx.Client(timeout=30) as client:
    response = client.get(f"https://api.telegram.org/bot{token}/getUpdates")
    response.raise_for_status()
    updates = response.json()["result"]

if not updates:
    raise SystemExit("Сообщения не найдены. Отправьте боту /start и повторите запуск.")

seen_chat_ids = set()

for update in updates:
    message = update.get("message") or update.get("channel_post")
    if not message:
        continue

    chat = message["chat"]
    chat_id = chat["id"]

    if chat_id in seen_chat_ids:
        continue

    seen_chat_ids.add(chat_id)
    chat_name = chat.get("title") or chat.get("username") or chat.get("first_name") or "Без имени"
    print(f"Chat ID: {chat_id} | Чат: {chat_name}")
