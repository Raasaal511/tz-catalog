# Invix Catalog — микросервис каталога товаров

Практическое тестовое задание **Invix Solutions** (код доступа: `INV-H2Y9B`).

Stateless-стек: **Telegram-бот (aiogram 3)** создаёт товары, **FastAPI** хранит метаданные в **PostgreSQL** и картинки в **MinIO (S3)**, **Next.js** показывает каталог в браузере и в **Telegram Mini App**.

```
Telegram ──► Bot (aiogram) ──► FastAPI ──► PostgreSQL
                     │              └──► MinIO
Telegram Mini App / Browser ──► Next.js ──► FastAPI
```

## Что реализовано

| Требование ТЗ | Реализация |
|---|---|
| Создать товар (название + фото в одном сообщении) | Админ шлёт photo + caption → бот → `POST /api/v1/products` |
| Каталог Next.js с заголовком «Каталог» | SSR-страница со списком товаров |
| Telegram Mini App | Кнопка `web_app` + инициализация Telegram WebApp SDK |
| FastAPI + PostgreSQL + MinIO + aiogram 3 | Отдельные сервисы в monorepo |
| Stateless / несколько инстансов | Нет локального FSM/файлов; bot в prod — **webhook**; общее состояние только в Postgres/MinIO |

## Структура репозитория

```
backend/     FastAPI (products + media proxy)
bot/         aiogram 3 (polling локально, webhook в prod)
frontend/    Next.js App Router (каталог)
docker-compose.yml
render.yaml  Blueprint для Render
```

## Быстрый старт (локально)

### 1. Подготовка

1. Создайте бота у [@BotFather](https://t.me/BotFather), получите `BOT_TOKEN`.
2. Узнайте свой Telegram ID (например, через [@userinfobot](https://t.me/userinfobot)).
3. Скопируйте env:

```bash
cp .env.example .env
```

Заполните минимум:

```env
BOT_TOKEN=...
ADMIN_TELEGRAM_IDS=123456789
INTERNAL_API_KEY=dev-internal-key
WEBAPP_URL=http://localhost:3000
PUBLIC_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
BOT_MODE=polling
```

> **Mini App и HTTPS:** Telegram открывает WebApp только по **HTTPS**.  
> Локально каталог открывается в браузере на `http://localhost:3000`.  
> Для настоящей кнопки Mini App пробросьте фронт через ngrok/cloudflared и укажите HTTPS URL в `WEBAPP_URL`.

### 2. Запуск всего стека

```bash
make up
# или: docker compose --env-file .env up --build -d
```

Сервисы:

| Сервис | URL |
|---|---|
| Каталог (Next.js) | http://localhost:3000 |
| API (FastAPI /docs) | http://localhost:8000/docs |
| MinIO API (host) | http://localhost:19000 |
| MinIO Console (host) | http://localhost:19001 (`minioadmin` / `minioadmin`) |
| Postgres (host, optional) | `localhost:15432` / user+db `catalog` |
| Bot health (webhook mode) | http://localhost:8080/health |

> Образ `minio/minio` с Docker Hub/Quay больше не отдаётся публично (2025–2026).  
> В compose используется drop-in `pgsty/minio` — тот же S3 API MinIO.

Проверка:

```bash
make smoke
make logs
```

Остановка:

```bash
make down
```

### 3. Как пользоваться ботом

1. Напишите боту `/start` → ответ **«У меня есть товар»** + кнопка каталога.
2. Админ (`ADMIN_TELEGRAM_IDS`): отправьте **одно сообщение** — фото + название в подписи.
3. Товар появится в каталоге на http://localhost:3000.

Команды:

- `/start`, `/help`, `/catalog` — приветствие и кнопка Mini App
- `/create` — подсказка по созданию товара (только админ)

## Архитектура и отказоустойчивость

### Stateless

- **API** — без локального диска и in-memory кэша; картинки только в MinIO, записи только в Postgres; `pool_pre_ping` для переживания reconnect.
- **Bot** — без MemoryStorage/FSM (создание товара атомарно: photo+caption). В production — **webhook** (несколько инстансов за LB безопасны). Polling — только для локальной разработки (один процесс).
- **Frontend** — SSR без серверной сессии; данные каждый раз с API.
- **Общее состояние** — PostgreSQL + MinIO (внешние shared stores).

### Границы сервисов

- Бот **не** пишет в БД/S3 напрямую — только через FastAPI (`X-API-Key`).
- Публичный список товаров — без ключа.
- Создание товара — только с `INTERNAL_API_KEY`.
- Медиа отдаётся через `GET /api/v1/media/{key}` (прокси из MinIO) — браузер не ходит в MinIO напрямую.

### Переменные окружения (ключевые)

| Переменная | Где | Назначение |
|---|---|---|
| `DATABASE_URL` | API | Postgres (`postgres://` с Render нормализуется в `postgresql+asyncpg://`) |
| `INTERNAL_API_KEY` | API + Bot | Секрет между ботом и API |
| `PUBLIC_BASE_URL` | API | Публичный URL API для ссылок на картинки |
| `S3_*` | API | MinIO endpoint / ключи / bucket |
| `BOT_TOKEN` | Bot | Токен Telegram |
| `ADMIN_TELEGRAM_IDS` | Bot | Кто может создавать товары |
| `WEBAPP_URL` | Bot | HTTPS URL Next.js для Mini App |
| `BOT_MODE` | Bot | `polling` \| `webhook` |
| `API_BASE_URL` | Bot / Frontend SSR | Базовый URL FastAPI |

## Деплой на Render

В репозитории есть `render.yaml` (Blueprint).

### Шаги

1. Запушьте репозиторий на GitHub/GitLab.
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → выберите репозиторий.
3. Дождитесь создания сервисов: `catalog-db`, `catalog-minio`, `catalog-api`, `catalog-bot`, `catalog-web`.
4. В настройках сервисов проставьте секреты/URL (после того как Render выдаст домены):

**catalog-api**

```text
PUBLIC_BASE_URL=https://<catalog-api>.onrender.com
CORS_ORIGINS=https://<catalog-web>.onrender.com
```

**catalog-bot**

```text
BOT_TOKEN=<token>
ADMIN_TELEGRAM_IDS=<your_id>
WEBAPP_URL=https://<catalog-web>.onrender.com
WEBHOOK_HOST=https://<catalog-bot>.onrender.com
BOT_MODE=webhook
```

**BotFather**

- Menu Button / Web App URL → `https://<catalog-web>.onrender.com`

5. Убедитесь, что `INTERNAL_API_KEY` совпадает у API и бота (в blueprint он шарится через `fromService`).

> Free-инстансы Render могут «засыпать». MinIO в blueprint на плане со диском — картинки переживают рестарт.

### Альтернатива без Blueprint

Создайте вручную PostgreSQL + 4 Web Services (Docker) из `backend/`, `bot/`, `frontend/` и образ MinIO с Persistent Disk на `/data`.

## Локальная разработка без Docker (опционально)

Нужны запущенные Postgres + MinIO (можно только их из compose):

```bash
docker compose up -d postgres minio
```

API:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://catalog:catalog@localhost:5432/catalog
export S3_ENDPOINT_URL=http://localhost:19000
export INTERNAL_API_KEY=dev-internal-key
export PUBLIC_BASE_URL=http://localhost:8000
uvicorn app.main:app --reload --port 8000
```

Bot:

```bash
cd bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN=...
export ADMIN_TELEGRAM_IDS=...
export API_BASE_URL=http://localhost:8000
export INTERNAL_API_KEY=dev-internal-key
export WEBAPP_URL=http://localhost:3000
export BOT_MODE=polling
python -m app.main
```

Frontend:

```bash
cd frontend
npm install
API_BASE_URL=http://localhost:8000 npm run dev
```

## API (кратко)

- `GET /health`
- `GET /api/v1/products` — список
- `POST /api/v1/products` — создание (`multipart`: `title`, `image`, опционально `created_by`), заголовок `X-API-Key`
- `GET /api/v1/media/{object_key}` — отдача изображения

## Форма сдачи (черновик)

- **Репозиторий:** https://github.com/Raasaal511/tz-catalog
- **Бот:** после создания у BotFather и деплоя `catalog-bot`
- **Стенд:** URL `catalog-web` на Render
- **Код доступа:** `INV-H2Y9B`

### Комментарий к сдаче (можно вставить в форму)

```text
Архитектура: Bot (aiogram 3, webhook) → FastAPI → PostgreSQL + MinIO(S3).
Каталог: Next.js App Router (SSR) + Telegram Mini App SDK.
Отказоустойчивость: все сервисы stateless; общее состояние только в Postgres/MinIO;
бот без MemoryStorage/FSM (создание товара атомарно photo+caption); в prod webhook.
Локальный запуск: cp .env.example .env && make up
Render: Blueprint render.yaml, затем проставить BOT_TOKEN / WEBAPP_URL / PUBLIC_BASE_URL.
```

## Лицензия

Учебный / assessment-проект.
