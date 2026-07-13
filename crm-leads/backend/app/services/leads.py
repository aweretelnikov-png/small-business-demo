from psycopg.rows import dict_row

from app.database import get_connection
from app.schemas import LeadCreate


def save_lead(lead: LeadCreate) -> int:

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
                    lead.phone,
                    lead.service,
                    lead.district.strip(),
                    lead.desired_date,
                    lead.comment.strip() if lead.comment else None,
                    lead.consent,
                ),
            )
            lead_id = cursor.fetchone()[0]

    return lead_id


def get_recent_leads(limit: int = 100) -> list[dict]:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    service,
                    district,
                    desired_date,
                    comment,
                    status,
                    crm_external_id,
                    created_at
                FROM leads
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()
