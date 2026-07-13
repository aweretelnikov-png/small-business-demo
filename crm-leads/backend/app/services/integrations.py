import logging

from app.schemas import LeadCreate
from app.services.leads import mark_crm_failed, mark_crm_synced
from app.services.telegram import (
    TelegramDeliveryError,
    send_lead_notification,
)
from app.services.twenty import TwentyAPIError, sync_lead_to_twenty

logger = logging.getLogger(__name__)


def process_lead_integrations(lead_id: int, lead: LeadCreate) -> None:
    try:
        send_lead_notification(lead_id, lead)
    except TelegramDeliveryError:
        logger.warning("Telegram notification failed for lead_id=%s", lead_id)

    try:
        opportunity_id = sync_lead_to_twenty(lead_id, lead)
        mark_crm_synced(lead_id, opportunity_id)
    except TwentyAPIError:
        mark_crm_failed(lead_id)
        logger.warning("Twenty synchronization failed for lead_id=%s", lead_id)
