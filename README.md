# brief-decoder

Прототип AI Brief Decoder. Пользователь вставляет текст клиентского брифа в
Chrome-расширение, бэкенд прогоняет его через LLM-провайдера, валидирует
структурированный ответ через Pydantic, сохраняет прогон в PostgreSQL и
возвращает результат в расширение.

Работает локально без платных API-ключей: по умолчанию включён fake-провайдер.

## Стек

- Backend: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), PostgreSQL
- Frontend: Chrome Extension на React + TypeScript (WXT)
- Тесты: pytest

## Как работает

```
Chrome Extension ──POST /v1/briefs/decode──► FastAPI
                                               │ провайдер (fake | real)
                                               │ Pydantic-валидация ответа
                                               │ запись прогона в Postgres
                 ◄──── result | safe error ────┘
GET /v1/briefs/runs/{id} — статус и результат прогона
```

Каждый вызов сохраняется как run: вход, статус, структурированный результат,
сырой ответ провайдера, безопасный код ошибки, таймстемпы. Наружу при сбое
уходит только safe-код (`PROVIDER_ERROR`, `VALIDATION_ERROR`) — сырой вывод
провайдера остаётся в БД для разбора.

## Запуск

```
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000, Swagger: http://localhost:8000/docs

### Расширение

```
cd extension
npm install
npm run build
```

Затем: `chrome://extensions` → включить Developer mode → Load unpacked →
указать папку сборки (`extension/.output/chrome-mv3`).

## Провайдеры

Выбор через переменную `LLM_PROVIDER` (по умолчанию `fake`).

### Fake-провайдер

Не требует ключей. Возвращает валидный разбор для любого текста. Сценарии
ошибок включаются ключевым словом в начале текста брифа:

| Ключевое слово       | Сценарий                                  |
|----------------------|-------------------------------------------|
| `FAIL:malformed`     | провайдер вернул некорректный JSON        |
| `FAIL:missing`       | JSON без обязательных полей               |
| `FAIL:severity`      | невалидное значение severity              |
| `FAIL:provider`      | сбой провайдера (исключение)              |

Любой другой текст → валидный структурированный результат.

### Реальный провайдер

Если настроен: указать `LLM_PROVIDER` и ключ в `.env` (см. `.env.example`).
Интерфейс провайдера один, реализация подключается конфигом.

## API

Создать прогон:

```
curl -X POST http://localhost:8000/v1/briefs/decode \
  -H "Content-Type: application/json" \
  -d '{"text": "We need a landing page for a B2B SaaS product..."}'
```

Получить прогон:

```
curl http://localhost:8000/v1/briefs/runs/<run_id>
```

Здоровье: `GET /health`

## Тесты

```
poetry run pytest
```

Покрывают: валидацию structured output (все сценарии), happy-path через API с
fake-провайдером, failure-path. Проверка расширения: `npm run build`
(typecheck + сборка).

## Структура

```
app/
├── config.py        # настройки (LLM_PROVIDER, DATABASE_URL)
├── database.py      # async engine + session
├── models.py        # таблица runs
├── schemas.py       # BriefDecodeResult и API-схемы
├── providers/       # base (интерфейс), fake, real
├── service.py       # decode: провайдер → валидация → сохранение
├── api/             # роуты
└── main.py
extension/           # Chrome Extension (WXT, React + TS)
tests/
```

## Assumptions & tradeoffs

- Обработка синхронная внутри запроса: объёмы прототипа не требуют очередей,
  run сохраняется в той же транзакции, что и ответ.
- Аутентификации нет — не входит в объём задания.
- См. также AI_USAGE.md — как в разработке использовался AI и как
  верифицировался его вывод.