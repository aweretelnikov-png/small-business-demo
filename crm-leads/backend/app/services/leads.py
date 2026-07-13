import re

from app.database import get_connection
from app.schemas import LeadCreate


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) != 11 or not digits.startswith("7"):
        raise ValueError("Некорректный российский телефон")

    return f"+{digits}"


def save_lead(lead: LeadCreate) -> int:
    normalized_phone = normalize_phone(lead.phone)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO leads (
                    name,
                    phone,
                    service,
                    district,
                    desired_date,
                    comment,
                    consent
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    lead.name.strip(),
                    normalized_phone,
                    lead.service,
                    lead.district.strip(),
                    lead.desired_date,
                    lead.comment.strip() if lead.comment else None,
                    lead.consent,
                ),
            )
            lead_id = cursor.fetchone()[0]

    return lead_id
