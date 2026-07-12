import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / "evaluation.env")

base_url = os.environ["OPEN_WEBUI_URL"].rstrip("/")
api_key = os.environ["OPEN_WEBUI_API_KEY"]
knowledge_id = os.environ["EVALUATION_KNOWLEDGE_ID"]

session = requests.Session()
session.trust_env = False

response = session.post(
    f"{base_url}/api/v1/retrieval/query/collection",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "collection_names": [knowledge_id],
        "query": "Сколько стоит замер по Москве?",
        "k": 5,
    },
    timeout=120,
)

if not response.ok:
    print(f"Ошибка retrieval API: HTTP {response.status_code}")
    print(response.text[:4000])
    raise SystemExit(1)

print(json.dumps(response.json(), ensure_ascii=False, indent=2)[:12000])
