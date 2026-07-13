from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import LeadCreate, LeadRead, LeadResponse
from app.services.integrations import process_lead_integrations
from app.services.leads import get_recent_leads, save_lead
from app.services.twenty_webhook import (
    process_twenty_webhook,
    verify_webhook_signature,
)

app = FastAPI(
    title="Фальшивые двери — API заявок",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/webhooks/twenty")
async def receive_twenty_webhook(
    request: Request,
    x_twenty_webhook_signature: str = Header(...),
    x_twenty_webhook_timestamp: str = Header(...),
) -> dict[str, str]:
    raw_body = await request.body()

    if not verify_webhook_signature(
        raw_body,
        x_twenty_webhook_signature,
        x_twenty_webhook_timestamp,
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid JSON") from error

    result = process_twenty_webhook(payload)
    return {"status": result}


@app.get("/api/leads", response_model=list[LeadRead])
def list_leads() -> list[LeadRead]:
    return [LeadRead(**lead) for lead in get_recent_leads()]


@app.post(
    "/api/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead: LeadCreate,
    background_tasks: BackgroundTasks,
) -> LeadResponse:
    lead_id = save_lead(lead)
    background_tasks.add_task(process_lead_integrations, lead_id, lead)
    return LeadResponse(lead_id=lead_id, status="created")
