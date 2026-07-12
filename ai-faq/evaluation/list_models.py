import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / "evaluation.env")

base_url = os.environ["OPEN_WEBUI_URL"].rstrip("/")
api_key = os.environ["OPEN_WEBUI_API_KEY"]

session = requests.Session()
session.trust_env = False

response = session.get(
    f"{base_url}/api/models?refresh=true",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=30,
)
if not response.ok:
    print(f"Ошибка Open WebUI API: HTTP {response.status_code}")
    print(response.text[:2000])
    raise SystemExit(1)

models = response.json().get("data", [])

print(f"Доступно моделей: {len(models)}")
for model in models:
    model_id = model.get("id", "<без id>")
    model_name = model.get("name") or model.get("info", {}).get("name") or "<без названия>"
    print(f"- ID: {model_id} | Название: {model_name}")
