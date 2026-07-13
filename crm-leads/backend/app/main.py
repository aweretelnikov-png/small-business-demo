from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import LeadCreate, LeadRead, LeadResponse
from app.services.leads import get_recent_leads, save_lead

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


@app.get("/api/leads", response_model=list[LeadRead])
def list_leads() -> list[LeadRead]:
    return [LeadRead(**lead) for lead in get_recent_leads()]


@app.post(
    "/api/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(lead: LeadCreate) -> LeadResponse:
    lead_id = save_lead(lead)
    return LeadResponse(lead_id=lead_id, status="created")
