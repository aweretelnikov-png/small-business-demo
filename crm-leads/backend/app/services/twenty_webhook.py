import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Any

from app.services.leads import update_lead_status_from_crm

STAGE_TO_STATUS = {
    "NOVAYA_ZAYAVKA": "new",
    "SVYAZALIS": "contacted",
    "NAZNACHEN_ZAMER": "measurement_scheduled",
    "PREDLOZHENIE_OTPRAVLENO": "proposal_sent",
    "OZHIDAETSYA_OPLATA": "awaiting_payment",
    "USPESHNO": "won",
    "OTKAZ": "lost",
}


def _parse_timestamp(value: str) -> datetime:
    try:
        numeric_value = float(value)
        if numeric_value > 10_000_000_000:
            numeric_value /= 1000
        return datetime.fromtimestamp(numeric_value, tz=timezone.utc)
    except ValueError:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def verify_webhook_signature(
    raw_body: bytes,
    signature: str,
    timestamp: str,
    max_age_seconds: int = 300,
) -> bool:
    secret = os.environ["TWENTY_WEBHOOK_SECRET"].encode()
    message = timestamp.encode() + b":" + raw_body
    expected = hmac.new(secret, message, hashlib.sha256).hexdigest()
    received = signature.removeprefix("sha256=")

    if not hmac.compare_digest(expected, received):
        return False

    try:
        signed_at = _parse_timestamp(timestamp)
    except (ValueError, OverflowError):
        return False

    age = abs((datetime.now(timezone.utc) - signed_at).total_seconds())
    return age <= max_age_seconds


def process_twenty_webhook(payload: dict[str, Any]) -> str:
    event_name = payload.get("eventName") or payload.get("event")
    if event_name != "opportunity.updated":
        return "ignored"

    data = payload.get("record") or payload.get("data")
    if not isinstance(data, dict):
        return "ignored"

    opportunity_id = data.get("id")
    stage = data.get("stage")
    new_status = STAGE_TO_STATUS.get(stage)

    if not isinstance(opportunity_id, str) or new_status is None:
        return "ignored"

    timestamp_value = (
        data.get("updatedAt")
        or payload.get("eventDate")
        or payload.get("timestamp")
    )
    if not isinstance(timestamp_value, str):
        return "ignored"

    try:
        changed_at = _parse_timestamp(timestamp_value)
    except (ValueError, OverflowError):
        return "ignored"

    return update_lead_status_from_crm(
        opportunity_id,
        new_status,
        changed_at,
    )
