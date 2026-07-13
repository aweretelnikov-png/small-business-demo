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
        f"{base_url}/rest/opportunities",
        headers=headers,
        params={"limit": 100},
    )
    response.raise_for_status()

payload = response.json()
data = payload["data"]

if isinstance(data, dict):
    records = data.get("opportunities", [])
else:
    records = data

opportunity = next(
    (
        record
        for record in records
        if record.get("vneshniyIdZayavki") == "manual-test-1"
    ),
    None,
)

if opportunity is None:
    raise SystemExit("Сделка manual-test-1 не найдена.")
print("Поля Opportunity:")
for field_name in sorted(opportunity):
    print(f"- {field_name}")

print("\nЗначения пользовательских полей:")
for field_name in (
    "stage",
    "vneshniyIdZayavki",
    "usluga",
    "istochnik",
    "rayon",
    "zhelaemayaData",
):
    print(f"{field_name}: {opportunity.get(field_name)!r}")
