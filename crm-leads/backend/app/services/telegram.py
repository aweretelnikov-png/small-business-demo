import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from app.schemas import LeadCreate

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

SERVICE_NAMES = {
    "false-door": "Фальшивая дверь",
    "hidden-door": "Скрытая дверь",
    "decorative-door": "Декоративная дверь",
}


class TelegramDeliveryError(Exception):
    pass


def send_telegram_message(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise TelegramDeliveryError("Не удалось отправить сообщение в Telegram") from error


def send_lead_notification(lead_id: int, lead: LeadCreate) -> None:
    desired_date = lead.desired_date.isoformat() if lead.desired_date else "Не указана"
    comment = lead.comment or "Нет"

    text = (
        f"Новая заявка №{lead_id}\n\n"
        f"Клиент: {lead.name}\n"
        f"Телефон: {lead.phone}\n"
        f"Услуга: {SERVICE_NAMES[lead.service]}\n"
        f"Район: {lead.district}\n"
        f"Желаемая дата: {desired_date}\n"
        f"Комментарий: {comment}"
    )

    send_telegram_message(text)
