import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / "evaluation.env")

base_url = os.environ["OPEN_WEBUI_URL"].rstrip("/")
api_key = os.environ["OPEN_WEBUI_API_KEY"]
model_id = os.environ["EVALUATION_MODEL_ID"]

session = requests.Session()
session.trust_env = False

response = session.get(
    f"{base_url}/api/v1/models/model",
    headers={"Authorization": f"Bearer {api_key}"},
    params={"id": model_id},
    timeout=30,
)

if not response.ok:
    print(f"Ошибка Open WebUI API: HTTP {response.status_code}")
    print(response.text[:4000])
    raise SystemExit(1)

print(json.dumps(response.json(), ensure_ascii=False, indent=2))
