import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

base_url = os.environ["TWENTY_BASE_URL"].rstrip("/")
headers = {"Authorization": f"Bearer {os.environ['TWENTY_API_KEY']}"}

with httpx.Client(timeout=30, trust_env=False) as client:
    response = client.get(
        f"{base_url}/rest/people",
        headers=headers,
        params={
            "limit": 1,
            "filter": "phones.primaryPhoneNumber[eq]:9990000001",
        },
    )
    response.raise_for_status()

payload = response.json()
data = payload["data"]
records = data.get("people", []) if isinstance(data, dict) else data

person = next(
    (
        record
        for record in records
        if "9990000001" in str(record.get("phones", ""))
    ),
    None,
)

if person is None:
    raise SystemExit("Тестовый контакт +79990000001 не найден.")

print(f"id: {person['id']}")
print(f"name: {person['name']!r}")
print(f"phones: {person['phones']!r}")
