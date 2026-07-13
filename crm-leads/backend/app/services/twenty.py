import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from app.schemas import LeadCreate

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

SERVICE_CODES = {
    "false-door": "FALSHIVAYA_DVER",
    "hidden-door": "SKRYTAYA_DVER",
    "decorative-door": "DEKORATIVNAYA_DVER",
}


class TwentyAPIError(Exception):
    pass


def _records(payload: dict[str, Any], plural_name: str) -> list[dict[str, Any]]:
    data = payload.get("data", [])

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        records = data.get(plural_name, [])
        return records if isinstance(records, list) else []

    return []


def _entity(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")

    if isinstance(data, dict) and "id" in data:
        return data
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, dict) and "id" in value:
                return value

    raise TwentyAPIError("Twenty вернул неожиданный формат ответа")


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    **kwargs: Any,
) -> dict[str, Any]:
    base_url = os.environ["TWENTY_BASE_URL"].rstrip("/")
    headers = {"Authorization": f"Bearer {os.environ['TWENTY_API_KEY']}"}

    try:
        response = client.request(
            method,
            f"{base_url}{path}",
            headers=headers,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise TwentyAPIError("Запрос к Twenty API завершился ошибкой") from error


def _find_opportunity(client: httpx.Client, lead_id: int) -> dict[str, Any] | None:
    payload = _request(
        client,
        "GET",
        "/rest/opportunities",
        params={
            "limit": 1,
            "filter": f"vneshniyIdZayavki[eq]:{lead_id}",
        },
    )
    records = _records(payload, "opportunities")
    return records[0] if records else None


def _find_person(client: httpx.Client, phone: str) -> dict[str, Any] | None:
    national_number = phone[2:]
    payload = _request(
        client,
        "GET",
        "/rest/people",
        params={
            "limit": 1,
            "filter": f"phones.primaryPhoneNumber[eq]:{national_number}",
        },
    )
    records = _records(payload, "people")
    return records[0] if records else None


def _create_person(client: httpx.Client, lead: LeadCreate) -> dict[str, Any]:
    name_parts = lead.name.strip().split(maxsplit=1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) == 2 else ""

    payload = _request(
        client,
        "POST",
        "/rest/people",
        json={
            "name": {
                "firstName": first_name,
                "lastName": last_name,
            },
            "phones": {
                "primaryPhoneNumber": lead.phone[2:],
                "primaryPhoneCountryCode": "RU",
                "primaryPhoneCallingCode": "+7",
                "additionalPhones": [],
            },
        },
    )
    return _entity(payload)


def _create_opportunity(
    client: httpx.Client,
    lead_id: int,
    lead: LeadCreate,
    person_id: str,
) -> dict[str, Any]:
    opportunity_data: dict[str, Any] = {
        "name": f"{lead.name} — заявка №{lead_id}",
        "stage": "NOVAYA_ZAYAVKA",
        "pointOfContactId": person_id,
        "vneshniyIdZayavki": str(lead_id),
        "usluga": SERVICE_CODES[lead.service],
        "istochnik": "SAYT",
        "rayon": lead.district,
        "kommentariyZayavki": lead.comment or "",
    }

    if lead.desired_date:
        opportunity_data["zhelaemayaData"] = lead.desired_date.isoformat()

    payload = _request(
        client,
        "POST",
        "/rest/opportunities",
        json=opportunity_data,
    )
    return _entity(payload)


def sync_lead_to_twenty(lead_id: int, lead: LeadCreate) -> str:
    with httpx.Client(timeout=30, trust_env=False) as client:
        existing_opportunity = _find_opportunity(client, lead_id)
        if existing_opportunity:
            return str(existing_opportunity["id"])

        person = _find_person(client, lead.phone)
        if person is None:
            person = _create_person(client, lead)

        opportunity = _create_opportunity(client, lead_id, lead, str(person["id"]))
        return str(opportunity["id"])
