<p align="center">
  <img src="brand/social-preview.png" alt="Voice Reminder Bot" width="100%" />
</p>

<h1 align="center">🔔 Voice Reminder Bot — Telegram bot + WebApp calendar</h1>

<p align="center">
  <a href="https://t.me/SayItRemindBot"><img src="https://img.shields.io/badge/Telegram-%40SayItRemindBot-2563EB?logo=telegram&logoColor=white" alt="Telegram bot" /></a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-async-059669?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-Vite%20%2B%20TS-61DAFB?logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Groq-Whisper%20%2B%20LLM-F55036?logo=groq&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/deploy-Railway-7C3AED?logo=railway&logoColor=white" alt="Railway" />
  <img src="https://img.shields.io/badge/license-MIT-94A3B8" alt="MIT" />
</p>

A reminder assistant for people who forget things. Send the bot a **voice** or
**text** message ("remind me tomorrow at 6pm to buy milk"); it transcribes the
speech, extracts *what* and *when*, stores it, and pings you at the right
moment. A **WebApp calendar** shows and lets you edit all your reminders.

The project is **multi-user**: anyone who sends `/start` is registered
automatically and only ever sees their own reminders.

👉 **Live bot:** [@SayItRemindBot](https://t.me/SayItRemindBot) — send `/start`.

---

## ✨ Features

- 🎙 **Voice → reminder**: Groq Whisper (`whisper-large-v3`) with automatic
  language detection (ru / uk / en / de / es / fr / pl / it and more, including
  mixed speech).
- 🧠 **Structured extraction** by an LLM (`llama-3.3-70b-versatile`): the *what*
  and the *when*, understanding relative time ("tomorrow", "in an hour",
  "morgen", "mañana", "next friday") in the user's timezone.
- ✍️ **Text works too** — the same pipeline as voice.
- ✅ **Confirmation** before saving: Save / Edit / Cancel.
- ⏰ **Delivery** at the scheduled time + Done / Snooze 1h buttons.
- 🔁 **Survives restarts**: APScheduler restores every future reminder from the
  database on startup, so a redeploy never loses a reminder.
- 📅 **WebApp calendar** (month / week / day / list): view, create, edit,
  delete, mark done. Reminders appear as color-coded dots.
- 🌍 **Multilingual** bot & WebApp (RU / EN / DE / UK / ES; easy to extend).
- 🌓 **Telegram theme** (light / dark) applied automatically.

---

## 🏗 Architecture

```
              voice / text
                   │
            ┌──────▼───────┐
            │ Telegram Bot │  python-telegram-bot (async, long polling)
            └──────┬───────┘
        voice ─────┤
                   ▼
         Groq Whisper (STT)  ──►  text
                   │
                   ▼
       Groq LLM (extract)  ──►  { title, datetime }
          + current time and the user's timezone
                   │
        confirmation  ✅ / ✏️ / ❌
                   ▼
        ┌──────────────────┐      ┌──────────────┐
        │   PostgreSQL     │◄────►│ APScheduler  │──► 🔔 delivery
        │  users           │      │  restore on  │    ✅ Done
        │  reminders       │      │  restart     │    ⏰ +1 hour
        └────────┬─────────┘      └──────────────┘
                 │
          ┌──────▼───────┐
          │   FastAPI    │  initData HMAC validation
          │  /api/...    │
          └──────┬───────┘
                 │
          ┌──────▼───────┐
          │   WebApp     │  React + Vite + react-big-calendar
          └──────────────┘
```

**The bot and the API run in a single process** (`app/main.py`) — one Railway
service. The WebApp is a separate static service.

### Project structure

```
bot/                     # Python: bot + API + scheduler
  app/
    config.py            # environment variables
    constants.py         # status/source as validated strings
    db/                  # engine, models (User, Reminder)
    services/            # stt, extract, reminders, users, scheduler, timeutils
    handlers/            # commands, messages (voice/text), callbacks
    i18n/                # locales RU/EN/DE/UK/ES
    api/                 # FastAPI: auth (initData), routes, schemas
    main.py              # runs everything in one process
  alembic/               # DB migrations
  Dockerfile
webapp/                  # React + Vite + TypeScript
  src/
    components/          # Calendar, ReminderModal, LangSwitch
    api.ts, telegram.ts, i18n.ts
  Dockerfile, nginx.conf
```

### Database

**users**: `id`, `telegram_id` (unique), `username`, `first_name`,
`timezone` (default `Europe/Berlin`), `language`, `created_at`.

**reminders**: `id`, `user_id` (FK), `title`, `remind_at` (timestamptz),
`status` (`pending`/`done`/`cancelled`), `source` (`voice`/`text`/`manual`),
`original_text`, `created_at`, `updated_at`.

`status` and `source` are stored as **validated strings** (not a native PG
enum), which keeps migrations simple.

---

## 🔑 Getting the keys (free)

### Telegram Bot Token
1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. `/newbot` → set a name and username → you get a **token** like `123456:ABC...`.
3. Nothing else is needed for the WebApp — its URL is passed via `WEBAPP_URL`.

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com) (free account).
2. **API Keys → Create API Key** → copy the `gsk_...` key.
3. Whisper and the LLM are available on the free tier.

---

## 💻 Running locally

### 1. PostgreSQL
Start a local database (e.g. in Docker):
```bash
docker run --name reminders-db -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=reminders -p 5432:5432 -d postgres:16
```

### 2. Bot + API
```bash
cd bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # fill in TELEGRAM_BOT_TOKEN, GROQ_API_KEY, DATABASE_URL
#   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reminders

alembic upgrade head        # create the tables
python -m app.main          # bot (polling) + API on :8000
```
> The voice fallback needs **ffmpeg** on the PATH (on most systems `.oga` is
> accepted by Groq directly; ffmpeg is just a safety net).

### 3. WebApp
```bash
cd webapp
npm install
cp .env.example .env         # VITE_API_URL=http://localhost:8000
npm run dev                  # http://localhost:5173
```
> The WebApp authenticates via Telegram `initData`, so it **only works fully
> when opened from Telegram** (the inline "📅 My reminders" button). Opened in a
> plain browser, the list stays empty (no valid initData).

### Smoke test
1. Send `/start` to the bot — you get registered and see the greeting.
2. Send a voice or text message: "remind me in 2 minutes to drink water".
3. Confirm "✅ Save" — at the scheduled time you get 🔔.

---

## 🚀 Deploy on Railway (free)

You need **3 components**: PostgreSQL, the bot service, the WebApp service.

### 1. PostgreSQL
In the Railway project: **New → Database → PostgreSQL**. Railway creates a
`DATABASE_URL` variable (the driver is normalized to `asyncpg` automatically in
`config.py`).

### 2. Bot service (`bot/`)
- **New → GitHub Repo** → Root Directory: `bot` (built from `bot/Dockerfile`,
  which runs `alembic upgrade head` before start).
- Environment variables:
  | Variable | Value |
  |---|---|
  | `TELEGRAM_BOT_TOKEN` | token from BotFather |
  | `GROQ_API_KEY` | Groq key |
  | `DATABASE_URL` | reference to the Postgres service |
  | `WEBAPP_URL` | public URL of the WebApp service (see step 3) |
- The bot uses long polling, so a public domain isn't strictly required — but
  the API needs one. Enable **Networking → Public Networking**; the app binds to
  Railway's `$PORT` automatically.

### 3. WebApp service (`webapp/`)
- **New → same repo** → Root Directory: `webapp` (built from `webapp/Dockerfile`,
  nginx).
- **Build variable** `VITE_API_URL` = the bot service's public URL
  (e.g. `https://reminder-bot.up.railway.app`).
- Enable Public Networking → you get a domain like
  `https://reminder-webapp.up.railway.app`.

### 4. Link them
- Set `WEBAPP_URL` in the bot service to the WebApp URL → redeploy the bot.
- No BotFather `/setdomain` is required: the WebApp opens from an **inline
  button** (`/start`, `/list`, `/app`), which delivers a valid `initData`.

The bot's `/start`, `/list` and `/app` messages then carry the "📅 My reminders"
button that opens the calendar.

---

## 🌐 Adding a language
- **Bot**: add a dictionary to `bot/app/i18n/locales.py`.
- **WebApp**: add an object to `STRINGS` in `webapp/src/i18n.ts`.

English is the fallback and the source of truth for the set of keys.

---

## 🖼 Screenshots (portfolio placeholders)

| Voice → reminder | Confirmation | WebApp calendar |
|---|---|---|
| _screenshot_ | _screenshot_ | _screenshot_ |

---

## 📋 Multi-user checklist
- [x] A user is created on first contact (`/start` or any message).
- [x] Every `reminders` query is filtered by `user_id`.
- [x] The API authenticates with the Telegram `initData` signature (you cannot
      act as another user).
- [x] No hardcoded Telegram IDs anywhere.
- [x] Timezone and language are per-user.

---

<details>
<summary>🇷🇺 <b>README на русском</b></summary>

<br>

Бот-помощник для тех, кто всё забывает. Пользователь присылает **голосовое**
или **текстовое** сообщение («напомни завтра в 6 вечера купить молоко»), бот
расшифровывает речь, извлекает суть и время, сохраняет в базу и присылает
уведомление в нужный момент. Есть **WebApp-календарь**, где все напоминания
видны и редактируемы.

Проект **multi-user**: любой, кто написал боту `/start`, автоматически
регистрируется и видит только свои напоминания.

👉 **Живой бот:** [@SayItRemindBot](https://t.me/SayItRemindBot) — напиши `/start`.

### ✨ Возможности

- 🎙 **Голос → напоминание**: Groq Whisper (`whisper-large-v3`) с автоопределением
  языка (ru / uk / en / de / es / fr / pl / it и др., включая смешанную речь).
- 🧠 **Извлечение структуры** LLM-ом (`llama-3.3-70b-versatile`): что напомнить +
  когда, с пониманием относительного времени («завтра», «через час», «morgen»,
  «mañana», «next friday») в таймзоне пользователя.
- ✍️ **Текст тоже работает** — тем же пайплайном, что и голос.
- ✅ **Подтверждение** перед сохранением: «Сохранить / Изменить / Отмена».
- ⏰ **Доставка** в назначенное время + кнопки «Готово / Отложить на час».
- 🔁 **Не теряет задачи** при рестарте: APScheduler восстанавливает все будущие
  напоминания из БД при старте.
- 📅 **WebApp-календарь** (месяц/неделя/день/список): просмотр, создание,
  редактирование, удаление, отметка «выполнено». Напоминания — цветные точки.
- 🌍 **Мультиязычность** бота и WebApp (RU / EN / DE / UK / ES; легко дописать).
- 🌓 **Тема Telegram** (светлая/тёмная) подхватывается автоматически.

### 🏗 Архитектура

**Бот и API запускаются в одном процессе** (`app/main.py`) — один сервис на
Railway. WebApp — отдельный статический сервис.

- `bot/app/` — `config`, `constants`, `db` (модели User/Reminder), `services`
  (stt, extract, reminders, users, scheduler, timeutils), `handlers` (commands,
  messages, callbacks), `i18n`, `api` (auth по initData, routes, schemas),
  `main.py`. Миграции — `alembic/`.
- `webapp/src/` — `components` (Calendar, ReminderModal, LangSwitch), `api.ts`,
  `telegram.ts`, `i18n.ts`.

**База данных.** `users`: `id`, `telegram_id` (unique), `username`,
`first_name`, `timezone` (деф. `Europe/Berlin`), `language`, `created_at`.
`reminders`: `id`, `user_id` (FK), `title`, `remind_at` (timestamptz),
`status` (`pending`/`done`/`cancelled`), `source` (`voice`/`text`/`manual`),
`original_text`, `created_at`, `updated_at`. `status` и `source` — строки с
валидацией в коде (не нативный PG enum), миграции остаются простыми.

### 🔑 Ключи (бесплатно)

- **Telegram Bot Token** — [@BotFather](https://t.me/BotFather) → `/newbot`.
- **Groq API Key** — [console.groq.com](https://console.groq.com) → API Keys →
  Create API Key (`gsk_...`). Whisper и LLM на бесплатном тарифе.

### 💻 Локальный запуск

```bash
# Postgres
docker run --name reminders-db -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=reminders -p 5432:5432 -d postgres:16

# Бот + API
cd bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # TELEGRAM_BOT_TOKEN, GROQ_API_KEY, DATABASE_URL
alembic upgrade head
python -m app.main          # бот (polling) + API на :8000

# WebApp
cd webapp
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev                 # http://localhost:5173
```
> Для голосового фолбэка нужен **ffmpeg** в PATH. WebApp авторизуется через
> Telegram `initData`, поэтому полноценно работает только при открытии из
> Telegram (inline-кнопка «📅 Мои напоминания»).

### 🚀 Деплой на Railway (бесплатно)

Три компонента: **PostgreSQL**, сервис бота (`bot/`), сервис WebApp (`webapp/`).

1. **PostgreSQL** — New → Database → PostgreSQL (создаст `DATABASE_URL`).
2. **Бот** — New → GitHub Repo → Root Directory `bot`. Переменные:
   `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `DATABASE_URL` (reference),
   `WEBAPP_URL`. Включи Public Networking — приложение само слушает `$PORT`.
3. **WebApp** — тот же репо, Root Directory `webapp`. Build-переменная
   `VITE_API_URL` = публичный URL бота. Включи Public Networking → получишь домен.
4. **Связать** — пропиши URL WebApp в `WEBAPP_URL` бота → redeploy. `/setdomain`
   в BotFather **не нужен**: WebApp открывается inline-кнопкой (`/start`, `/list`,
   `/app`), которая отдаёт валидный `initData`.

### 🌐 Добавить язык
- **Бот**: словарь в `bot/app/i18n/locales.py`.
- **WebApp**: объект в `STRINGS` в `webapp/src/i18n.ts`.
- Английский — фолбэк и источник истины по набору ключей.

### 📋 Чеклист multi-user
- [x] Пользователь создаётся на первом контакте.
- [x] Все запросы к `reminders` фильтруются по `user_id`.
- [x] API авторизуется по подписи Telegram `initData`.
- [x] Никаких захардкоженных Telegram ID.
- [x] Таймзона и язык — на пользователя.

</details>
