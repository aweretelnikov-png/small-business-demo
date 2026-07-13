from app.schemas import LeadCreate
from app.services.leads import (
    get_leads_for_crm_sync,
    mark_crm_failed,
    mark_crm_synced,
)
from app.services.twenty import TwentyAPIError, sync_lead_to_twenty

leads = get_leads_for_crm_sync()

if not leads:
    raise SystemExit("Заявок для синхронизации нет.")

for lead_data in leads:
    lead_id = lead_data.pop("id")
    lead = LeadCreate(**lead_data)

    try:
        opportunity_id = sync_lead_to_twenty(lead_id, lead)
        mark_crm_synced(lead_id, opportunity_id)
        print(f"Заявка {lead_id}: synced")
    except TwentyAPIError:
        mark_crm_failed(lead_id)
        print(f"Заявка {lead_id}: failed")
