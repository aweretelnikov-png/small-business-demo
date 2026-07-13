from app.schemas import LeadCreate
from app.services.integrations import process_lead_integrations
from app.services.telegram import TelegramDeliveryError
from app.services.twenty import TwentyAPIError


def make_lead() -> LeadCreate:
    return LeadCreate(
        name="Иван",
        phone="+7 999 111-22-33",
        service="hidden-door",
        district="Москва",
        consent=True,
    )


def test_twenty_sync_continues_when_telegram_fails(monkeypatch) -> None:
    result = {}

    def fail_telegram(lead_id, lead) -> None:
        raise TelegramDeliveryError("Telegram unavailable")

    monkeypatch.setattr(
        "app.services.integrations.send_lead_notification",
        fail_telegram,
    )
    monkeypatch.setattr(
        "app.services.integrations.sync_lead_to_twenty",
        lambda lead_id, lead: "opportunity-42",
    )
    monkeypatch.setattr(
        "app.services.integrations.mark_crm_synced",
        lambda lead_id, crm_id: result.update(status="synced", crm_id=crm_id),
    )

    process_lead_integrations(42, make_lead())

    assert result == {"status": "synced", "crm_id": "opportunity-42"}


def test_failed_twenty_sync_is_recorded(monkeypatch) -> None:
    result = {}

    monkeypatch.setattr(
        "app.services.integrations.send_lead_notification",
        lambda lead_id, lead: None,
    )

    def fail_twenty(lead_id, lead) -> str:
        raise TwentyAPIError("Twenty unavailable")

    monkeypatch.setattr(
        "app.services.integrations.sync_lead_to_twenty",
        fail_twenty,
    )
    monkeypatch.setattr(
        "app.services.integrations.mark_crm_failed",
        lambda lead_id: result.update(status="failed", lead_id=lead_id),
    )

    process_lead_integrations(43, make_lead())

    assert result == {"status": "failed", "lead_id": 43}
