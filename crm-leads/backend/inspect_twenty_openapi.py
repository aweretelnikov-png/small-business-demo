import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

base_url = os.environ["TWENTY_BASE_URL"].rstrip("/")
headers = {"Authorization": f"Bearer {os.environ['TWENTY_API_KEY']}"}

with httpx.Client(timeout=30, trust_env=False) as client:
    response = client.get(f"{base_url}/open-api/core", headers=headers)
    response.raise_for_status()
    schema = response.json()

fields_to_find = {"stage", "usluga", "istochnik"}
found = {}


def walk(value) -> None:
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            for field_name in fields_to_find:
                field_schema = properties.get(field_name)
                if isinstance(field_schema, dict) and "enum" in field_schema:
                    found[field_name] = field_schema["enum"]
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


walk(schema)

for field_name in sorted(fields_to_find):
    print(f"{field_name}: {found.get(field_name, 'enum не найден')}")
