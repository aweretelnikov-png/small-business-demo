# AI FAQ

Учебный AI-ассистент для компании «Фальшивые двери». Ассистент отвечает на вопросы по базе знаний о услугах, ценах, гарантии, территории работы и оформлении заказа.

## Архитектура

```text
Markdown-документы
    ↓
Open WebUI: база знаний и embeddings
    ↓
LLM: OpenRouter или Ollama / Ollama Cloud
    ↓
Ответ с источниками
```

## Запуск

```cmd
cd ai-faq
docker compose up -d
docker compose ps
```

Open WebUI доступен по адресу: <http://localhost:3001>.

## Остановка

```cmd
docker compose stop
```

## Логи

```cmd
docker compose logs --tail=50 open-webui
```

## База знаний

Исходные документы находятся в [`knowledge/`](knowledge/):

- услуги;
- цены и порядок оплаты;
- гарантия;
- территория работы;
- оформление заказа;
- контакты;
- FAQ.

После изменения Markdown-файлов нужно заново загрузить или переиндексировать их в Open WebUI.

## Backup Open WebUI

```cmd
cd ai-faq
mkdir backups
docker run --rm -v ai-faq_open_webui_data:/data -v "%CD%\backups:/backup" alpine tar -czf /backup/open-webui_backup.tar.gz -C /data .
```

Архив содержит чаты, настройки подключений, загруженные документы и embeddings. Он не добавляется в Git.

## Подключение модели

В учебном стенде протестированы:

- Free Models Router через OpenRouter;
- локальные Ollama-модели;
- Ollama Cloud.

API-ключи не хранятся в репозитории. Файл `OPEN_ROUTER_API_KEY.env` локальный и игнорируется Git.

## Тестирование

- 50 клиентских тестов: [`tests/questions.md`](tests/questions.md)
- Тесты внутреннего помощника: [`tests/internal_questions.md`](tests/internal_questions.md)
- Итоговый отчёт: [`tests/report.md`](tests/report.md)
- Переиспользуемый автотестер: [`evaluation/`](evaluation/)

Текущая клиентская конфигурация прошла 50 из 50 тестов после итеративного улучшения документов и retrieval.

Пример запуска партии:

```cmd
cd ai-faq
.venv-evaluation\Scripts\activate
python evaluation\run_tests.py --start 1 --limit 5
```

После изменения документов, модели, embeddings, системной инструкции или RAG Template тесты нужно запускать заново.

## Ограничения

Бесплатные модели могут иметь лимиты, показывать reasoning или нестабильно вызывать инструмент базы знаний. Не использовать реальные персональные данные клиентов в тестах с облачными моделями.

Для русскоязычных документов используется `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` и гибридный поиск. Автотестер выполняет retrieval отдельно от генерации, чтобы различать ошибки поиска и ошибки модели.
