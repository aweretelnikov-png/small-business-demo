# Автотесты AI FAQ

Переиспользуемый инструмент для проверки RAG-ассистентов через Open WebUI API.

## Возможности

- читает тесты из Markdown-таблицы;
- запускает выбранный диапазон;
- выполняет retrieval отдельно от генерации;
- сохраняет документы, источники, scores, reasoning и время;
- создаёт JSON и Markdown-отчёты;
- не публикует API-ключи и локальные результаты.

## Подготовка

Создать `ai-faq/evaluation.env`:

```env
OPEN_WEBUI_URL=http://localhost:3001
OPEN_WEBUI_API_KEY=<local-api-key>
EVALUATION_MODEL_ID=<custom-model-id>
EVALUATION_KNOWLEDGE_ID=<knowledge-id>
```

Файл `.env` не добавляется в Git.

Создать окружение:

```cmd
cd ai-faq
python -m venv .venv-evaluation
.venv-evaluation\Scripts\activate
pip install -r evaluation\requirements.txt
```

## Диагностика

```cmd
python evaluation\list_models.py
python evaluation\inspect_model.py
python evaluation\test_retrieval.py
python evaluation\test_chat.py
```

## Запуск тестов

Первые пять:

```cmd
python evaluation\run_tests.py --start 1 --limit 5
```

Следующие пять:

```cmd
python evaluation\run_tests.py --start 6 --limit 5
```

Все 50 тестов можно запустить так:

```cmd
python evaluation\run_tests.py --start 1 --limit 50
```

На бесплатном облачном тарифе рекомендуется запускать партиями по 5–10 вопросов.

## Результаты

Отчёты создаются в:

```text
ai-faq/evaluation/results/
```

Папка локальная и игнорируется Git, потому что при работе с реальными клиентами ответы могут содержать конфиденциальную информацию.

## Статусы

- `PASS_CANDIDATE` — предварительно успешный отказ для вопроса вне базы;
- `FAIL_CANDIDATE` — модель отказалась, хотя ожидался ответ из документов;
- `REVIEW` — содержательный ответ требует проверки;
- `ERROR` — техническая ошибка API.

Финальный `PASS/FAIL` устанавливается после проверки ответа человеком или отдельным надёжным evaluator.
