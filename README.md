# brief-decoder

Прототип AI Brief Decoder. Пользователь вставляет текст клиентского брифа в
Chrome-расширение, бэкенд прогоняет его через LLM-провайдера, валидирует
структурированный ответ через Pydantic, сохраняет прогон в PostgreSQL и
возвращает результат в расширение.

Работает локально без платных API-ключей: по умолчанию включён fake-провайдер.

## Стек

- Backend: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), PostgreSQL, Poetry
- Frontend: Chrome Extension — WXT, React + TypeScript
- Тесты: pytest

## Как работает

```
Chrome Extension ──POST /v1/briefs/decode──► FastAPI
                                               │ провайдер (fake по умолчанию)
                                               │ Pydantic-валидация structured output
                                               │ запись прогона (run) в Postgres
                 ◄──── result | safe error ────┘
GET /v1/briefs/runs/{id} — прогон по id
GET /health
```

Каждый вызов сохраняется как run: вход, статус, структурированный результат,
сырой ответ провайдера, safe-код ошибки, таймстемп. Наружу при сбое уходит
только safe-код (`provider_error`, `validation_error`) и фиксированное
сообщение — сырой вывод провайдера и стектрейсы остаются в БД для разбора.

Decode отвечает 200 и для упавших прогонов: сбой провайдера/валидации — это
бизнес-исход run'а (`status: failed` + `error_code` в теле), а не ошибка
HTTP-слоя. Клиент разбирает один формат ответа и ветвится по `status`.

## Запуск бэкенда

Требуется Docker.

```
docker compose up --build
```

Поднимает postgres и api. Таблицы создаются автоматически при старте
приложения. API: http://localhost:8000, Swagger: http://localhost:8000/docs

Быстрая проверка:

```
curl http://localhost:8000/health
curl -X POST http://localhost:8000/v1/briefs/decode \
  -H "Content-Type: application/json" \
  -d '{"text": "We need a landing page for a B2B SaaS analytics product"}'
curl http://localhost:8000/v1/briefs/runs/1
```

## Запуск расширения

Требуется Node.js 18+.

```
cd extension
npm install
npm run build
```

Затем в Chrome: `chrome://extensions` → включить **Developer mode** →
**Load unpacked** → выбрать папку `extension/.output/chrome-mv3`.

Открыть попап расширения, вставить текст брифа, нажать **Decode brief**.
Бэкенд должен быть запущен (расширение ходит на `http://localhost:8000`).

Для разработки: `npm run dev` (сборка в `.output/chrome-mv3-dev` с
пересборкой на изменения; авто-запуск браузера отключён — расширение
загружается вручную так же, через Load unpacked).

## Провайдеры

Выбор через переменную `LLM_PROVIDER` (по умолчанию `fake`, задана в
docker-compose). Провайдеры реализуют общий интерфейс
(`app/providers/base.py`), подключаются фабрикой по конфигу.

### Fake-провайдер

Ключей не требует. На обычный текст возвращает валидный структурированный
разбор. Сценарии ошибок включаются ключевым словом в начале текста брифа —
это позволяет продемонстрировать error state и в API, и в расширении:

| Текст начинается с | Сценарий                                    |
|--------------------|---------------------------------------------|
| `FAIL:malformed`   | провайдер вернул синтаксически кривой JSON  |
| `FAIL:missing`     | валидный JSON без обязательных полей        |
| `FAIL:severity`    | невалидное значение severity                |
| `FAIL:provider`    | сбой провайдера (исключение)                |

Пример:

```
curl -X POST http://localhost:8000/v1/briefs/decode \
  -H "Content-Type: application/json" \
  -d '{"text": "FAIL:provider test"}'
```

### Реальный провайдер

Не реализован (см. tradeoffs). Точка расширения готова: реализация
интерфейса `LLMProvider` + один case в фабрике `app/providers/__init__.py` +
значение `LLM_PROVIDER` и ключ в окружении.

## Тесты

Бэкенд (БД замокана, Postgres для тестов не нужен):

```
poetry install
poetry run pytest
```

Покрытие: валидация structured output (валидный / malformed / missing fields /
invalid severity — каждый со своим типом ошибки), happy-path API с
fake-провайдером, failure-paths (сбой провайдера, сбой валидации), пустой
вход, roundtrip POST→GET, 404.

Фронтенд (typecheck + сборка):

```
cd extension && npm run build
```

## Структура

```
app/
├── config.py        # настройки (DATABASE_URL, LLM_PROVIDER)
├── database.py      # async engine + session maker
├── models.py        # таблица runs, enums статуса и кодов ошибок
├── schemas.py       # BriefDecodeResult (structured output) + API-схемы
├── repository.py    # доступ к данным (stateless, сессия аргументом)
├── service.py       # decode: провайдер → валидация → safe-маппинг → запись
├── providers/       # base (Protocol), fake, фабрика по конфигу
├── api/             # роуты + зависимости
└── main.py          # приложение, CORS, create_all на старте
extension/
└── entrypoints/popup/   # App.tsx (UI-состояния), api.ts (контракт бэкенда)
tests/
├── conftest.py      # TestClient + мок сессии БД
├── test_validation.py
└── test_api.py
```

## Assumptions & tradeoffs

- **create_all вместо миграций**: схему создаёт приложение на старте.
  Осознанное упрощение прототипа (одна таблица, один инстанс); в продакшене —
  Alembic.
- **Синхронная обработка в запросе**: без очередей и фоновых воркеров —
  объёмы прототипа этого не требуют, run пишется в той же транзакции.
- **200 для failed-ранов**: сбой провайдера — данные run'а, не HTTP-ошибка
  (детали выше в «Как работает»).
- **CORS `*`**: id расширения генерируется при установке и заранее неизвестен;
  API без аутентификации и кук, поверхность риска нулевая. В продакшене —
  сузить до конкретного `chrome-extension://<id>`.
- **Реальный LLM-провайдер не реализован**: приоритет — end-to-end slice и
  качество fake-пути, по которому проходит ревью; интерфейс и фабрика готовы.
- **Аутентификации нет** — вне объёма задания.

## AI usage

Проект написан в паре с AI — процесс, границы делегирования и найденные
ошибки описаны в [AI_USAGE.md](AI_USAGE.md).