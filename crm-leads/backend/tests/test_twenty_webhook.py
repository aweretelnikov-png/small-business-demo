import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.services.twenty_webhook import (
    process_twenty_webhook,
    verify_webhook_signature,
)

client = TestClient(app)


def sign(secret: str, timestamp: str, body: bytes) -> str:
    return hmac.new(
        secret.encode(),
        timestamp.encode() + b":" + body,
        hashlib.sha256,
    ).hexdigest()


def test_valid_webhook_signature(monkeypatch) -> None:
    secret = "test-secret"
    timestamp = datetime.now(timezone.utc).isoformat()
    body = b'{"event":"opportunity.updated"}'
    monkeypatch.setenv("TWENTY_WEBHOOK_SECRET", secret)

    assert verify_webhook_signature(
        body,
        sign(secret, timestamp, body),
        timestamp,
    )


def test_invalid_webhook_signature(monkeypatch) -> None:
    monkeypatch.setenv("TWENTY_WEBHOOK_SECRET", "test-secret")
    timestamp = datetime.now(timezone.utc).isoformat()

    assert not verify_webhook_signature(b"{}", "invalid", timestamp)


def test_expired_webhook_is_rejected(monkeypatch) -> None:
    secret = "test-secret"
    timestamp = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    body = b"{}"
    monkeypatch.setenv("TWENTY_WEBHOOK_SECRET", secret)

    assert not verify_webhook_signature(
        body,
        sign(secret, timestamp, body),
        timestamp,
    )


def test_opportunity_stage_is_mapped(monkeypatch) -> None:
    captured = {}

    def fake_update(crm_external_id, new_status, changed_at) -> str:
        captured["crm_external_id"] = crm_external_id
        captured["new_status"] = new_status
        return "updated"

    monkeypatch.setattr(
        "app.services.twenty_webhook.update_lead_status_from_crm",
        fake_update,
    )

    result = process_twenty_webhook(
        {
            "event": "opportunity.updated",
            "data": {
                "id": "opportunity-42",
                "stage": "NAZNACHEN_ZAMER",
                "updatedAt": "2026-07-14T10:00:00Z",
            },
            "timestamp": "2026-07-14T10:00:01Z",
        }
    )

    assert result == "updated"
    assert captured == {
        "crm_external_id": "opportunity-42",
        "new_status": "measurement_scheduled",
    }


def test_current_twenty_payload_format_is_supported(monkeypatch) -> None:
    captured = {}

    def fake_update(crm_external_id, new_status, changed_at) -> str:
        captured["new_status"] = new_status
        return "updated"

    monkeypatch.setattr(
        "app.services.twenty_webhook.update_lead_status_from_crm",
        fake_update,
    )

    result = process_twenty_webhook(
        {
            "eventName": "opportunity.updated",
            "record": {
                "id": "opportunity-42",
                "stage": "SVYAZALIS",
                "updatedAt": "2026-07-14T10:00:00Z",
            },
            "eventDate": "2026-07-14T10:00:01Z",
        }
    )

    assert result == "updated"
    assert captured["new_status"] == "contacted"
