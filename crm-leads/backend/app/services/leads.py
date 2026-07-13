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


def mark_crm_synced(lead_id: int, crm_external_id: str) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE leads
                SET
                    crm_external_id = %s,
                    crm_sync_status = 'synced',
                    crm_sync_error = NULL,
                    crm_synced_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (crm_external_id, lead_id),
            )


def mark_crm_failed(lead_id: int) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE leads
                SET
                    crm_sync_status = 'failed',
                    crm_sync_error = 'Twenty API request failed',
                    updated_at = NOW()
                WHERE id = %s
                """,
                (lead_id,),
            )


def update_lead_status_from_crm(
    crm_external_id: str,
    new_status: str,
    changed_at,
) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, status
                FROM leads
                WHERE crm_external_id = %s
                FOR UPDATE
                """,
                (crm_external_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return "not_found"

            lead_id, old_status = row
            if old_status == new_status:
                return "unchanged"

            cursor.execute(
                """
                UPDATE leads
                SET
                    status = %s,
                    status_updated_at = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (new_status, changed_at, lead_id),
            )
            cursor.execute(
                """
                INSERT INTO lead_status_history (
                    lead_id,
                    old_status,
                    new_status,
                    source,
                    changed_at
                )
                VALUES (%s, %s, %s, 'twenty_webhook', %s)
                ON CONFLICT (lead_id, new_status, changed_at) DO NOTHING
                """,
                (lead_id, old_status, new_status, changed_at),
            )

    return "updated"


def get_leads_for_crm_sync(limit: int = 100) -> list[dict]:
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
                    consent
                FROM leads
                WHERE crm_external_id IS NULL
                  AND crm_sync_status IN ('pending', 'failed')
                ORDER BY created_at
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()


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
