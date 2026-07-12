import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEST_FILE = PROJECT_DIR / "tests" / "questions.md"
RESULTS_DIR = PROJECT_DIR / "evaluation" / "results"
FALLBACK_TEXT = "У меня нет подтверждённой информации по этому вопросу"


def load_settings() -> dict[str, str]:
    load_dotenv(PROJECT_DIR / "evaluation.env")
    required = [
        "OPEN_WEBUI_URL",
        "OPEN_WEBUI_API_KEY",
        "EVALUATION_MODEL_ID",
        "EVALUATION_KNOWLEDGE_ID",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(f"Не заданы переменные: {', '.join(missing)}")

    return {name: os.environ[name] for name in required}


def parse_tests(path: Path) -> list[dict]:
    tests = []
    row_pattern = re.compile(r"^\|\s*(\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|$")

    for line in path.read_text(encoding="utf-8").splitlines():
        match = row_pattern.match(line)
        if not match:
            continue

        number, category, question, expected, source, _status = [
            value.strip() for value in match.groups()
        ]
        tests.append(
            {
                "number": int(number),
                "category": category,
                "question": question,
                "expected": expected,
                "expected_source": source.strip("`"),
            }
        )

    return tests


def flatten_retrieval(payload: dict) -> tuple[list[str], list[str], list[float]]:
    documents = [item for group in payload.get("documents", []) for item in group]
    distances = [item for group in payload.get("distances", []) for item in group]
    sources = []

    for group in payload.get("metadatas", []):
        for metadata in group:
            source = metadata.get("source") or metadata.get("name")
            if source and source not in sources:
                sources.append(source)

    return documents, sources, distances


def retrieve(session: requests.Session, settings: dict[str, str], question: str) -> dict:
    response = session.post(
        f"{settings['OPEN_WEBUI_URL'].rstrip('/')}/api/v1/retrieval/query/collection",
        headers={
            "Authorization": f"Bearer {settings['OPEN_WEBUI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "collection_names": [settings["EVALUATION_KNOWLEDGE_ID"]],
            "query": question,
            "k": 5,
        },
        timeout=120,
    )
    response.raise_for_status()
    documents, sources, distances = flatten_retrieval(response.json())
    return {"documents": documents, "sources": sources, "scores": distances}


def build_user_message(question: str, documents: list[str]) -> str:
    context = "\n\n---\n\n".join(documents)
    return f"""Ответь на вопрос только по контексту ниже.
Не используй собственные знания и не добавляй неподтверждённые факты.
Сохраняй слова «от», «до», «после замера» и «индивидуально».
Если точного ответа в контексте нет, используй установленную фразу отказа.

<context>
{context}
</context>

Вопрос пользователя: {question}"""


def complete(
    session: requests.Session,
    settings: dict[str, str],
    question: str,
    documents: list[str],
) -> dict:
    started = time.perf_counter()
    response = session.post(
        f"{settings['OPEN_WEBUI_URL'].rstrip('/')}/api/chat/completions",
        headers={
            "Authorization": f"Bearer {settings['OPEN_WEBUI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings["EVALUATION_MODEL_ID"],
            "messages": [
                {
                    "role": "user",
                    "content": build_user_message(question, documents),
                }
            ],
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    elapsed = round(time.perf_counter() - started, 2)
    payload = response.json()
    message = payload["choices"][0]["message"]
    return {
        "answer": message.get("content", ""),
        "reasoning": message.get("reasoning_content", ""),
        "elapsed_seconds": elapsed,
        "usage": payload.get("usage", {}),
    }


def preliminary_status(test: dict, retrieval: dict, answer: str) -> str:
    expected_source = test["expected_source"]
    fallback_used = FALLBACK_TEXT.lower() in answer.lower()

    if expected_source == "—":
        return "PASS_CANDIDATE" if fallback_used else "REVIEW"

    if fallback_used:
        return "FAIL_CANDIDATE"

    return "REVIEW"


def write_reports(results: list[dict], model_id: str) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = RESULTS_DIR / f"evaluation_{timestamp}.json"
    md_path = RESULTS_DIR / f"evaluation_{timestamp}.md"

    json_path.write_text(
        json.dumps({"model": model_id, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Автоматический отчёт AI FAQ",
        "",
        f"Модель: `{model_id}`",
        "",
        "> `PASS_CANDIDATE` и `FAIL_CANDIDATE` — предварительные статусы. Критичные ответы нужно проверить вручную.",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"## Тест {result['number']} — {result['preliminary_status']}",
                "",
                f"**Категория:** {result['category']}",
                "",
                f"**Вопрос:** {result['question']}",
                "",
                f"**Ожидание:** {result['expected']}",
                "",
                f"**Источники retrieval:** {', '.join(result['retrieval']['sources']) or 'нет'}",
                "",
                f"**Время:** {result['completion']['elapsed_seconds']} сек.",
                "",
                "**Ответ:**",
                "",
                result["completion"]["answer"],
                "",
                "---",
                "",
            ]
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Пакетное тестирование AI FAQ.")
    parser.add_argument("--start", type=int, default=1, help="Номер первого теста")
    parser.add_argument("--limit", type=int, default=5, help="Количество тестов")
    parser.add_argument("--test-file", type=Path, default=DEFAULT_TEST_FILE)
    arguments = parser.parse_args()

    settings = load_settings()
    tests = [test for test in parse_tests(arguments.test_file) if test["number"] >= arguments.start]
    tests = tests[: arguments.limit]

    if not tests:
        raise ValueError("Для заданного диапазона тесты не найдены.")

    session = requests.Session()
    session.trust_env = False
    results = []

    for test in tests:
        print(f"[{test['number']}] {test['question']}")
        try:
            retrieval = retrieve(session, settings, test["question"])
            completion = complete(
                session,
                settings,
                test["question"],
                retrieval["documents"],
            )
            status = preliminary_status(test, retrieval, completion["answer"])
            print(f"    {status}, {completion['elapsed_seconds']} сек.")
            results.append(
                {
                    **test,
                    "preliminary_status": status,
                    "retrieval": retrieval,
                    "completion": completion,
                }
            )
        except Exception as error:
            print(f"    ERROR: {error}")
            results.append({**test, "preliminary_status": "ERROR", "error": str(error)})

    json_path, md_path = write_reports(results, settings["EVALUATION_MODEL_ID"])
    print(f"\nJSON: {json_path}")
    print(f"Markdown: {md_path}")


if __name__ == "__main__":
    main()
