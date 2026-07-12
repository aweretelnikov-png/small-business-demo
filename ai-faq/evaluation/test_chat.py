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
knowledge_id = os.environ["EVALUATION_KNOWLEDGE_ID"]

session = requests.Session()
session.trust_env = False

response = session.post(
    f"{base_url}/api/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": "Сколько стоит замер по Москве?",
            }
        ],
        "stream": False,
        "files": [
            {
                "id": knowledge_id,
                "type": "collection",
                "status": "processed",
            }
        ],
        "features": {
            "web_search": False,
            "code_interpreter": False,
            "image_generation": False,
            "memory": False,
        },
    },
    timeout=300,
)

if not response.ok:
    print(f"Ошибка Open WebUI API: HTTP {response.status_code}")
    print(response.text[:4000])
    raise SystemExit(1)

payload = response.json()
answer = payload["choices"][0]["message"]["content"]

print("=== Ответ ===")
print(answer)
print("\n=== Метаданные ответа ===")
print(json.dumps(payload, ensure_ascii=False, indent=2)[:8000])
