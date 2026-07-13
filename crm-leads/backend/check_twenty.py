import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

base_url = os.environ["TWENTY_BASE_URL"].rstrip("/")
api_key = os.environ["TWENTY_API_KEY"]

with httpx.Client(timeout=30, trust_env=False) as client:
    response = client.get(
        f"{base_url}/rest/people",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"limit": 1},
    )

print(f"HTTP status: {response.status_code}")
response.raise_for_status()
print(f"Ключи ответа: {', '.join(response.json().keys())}")
print("Twenty API доступен.")
