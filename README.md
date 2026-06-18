# 🔔 Голосовые напоминания — Telegram-бот + WebApp-календарь

Бот-помощник для тех, кто всё забывает. Пользователь присылает **голосовое**
или **текстовое** сообщение («напомни завтра в 6 вечера купить молоко»), бот
расшифровывает речь, извлекает суть и время, сохраняет в базу и присылает
уведомление в нужный момент. Есть **WebApp-календарь**, где все напоминания
видны и редактируемы.

Проект **multi-user**: любой, кто написал боту `/start`, автоматически
регистрируется и видит только свои напоминания.

---

## ✨ Возможности

- 🎙 **Голос → напоминание**: Groq Whisper (`whisper-large-v3`) с
  автоопределением языка (ru / uk / en / de / es / fr / pl / it и др.,
  включая смешанную речь).
- 🧠 **Извлечение структуры** LLM-ом (`llama-3.3-70b-versatile`): что напомнить
  + когда, с пониманием относительного времени («завтра», «через час»,
  «morgen», «mañana», «next friday») в таймзоне пользователя.
- ✍️ **Текст тоже работает** — тем же пайплайном, что и голос.
- ✅ **Подтверждение** перед сохранением: «Сохранить / Изменить / Отмена».
- ⏰ **Доставка** в назначенное время + кнопки «Готово / Отложить на час».
- 🔁 **Не теряет задачи** при рестарте: APScheduler восстанавливает все будущие
  напоминания из БД при старте.
- 📅 **WebApp-календарь** (месяц/неделя/день/список): просмотр, создание,
  редактирование, удаление, отметка «выполнено».
- 🌍 **Мультиязычность** бота и WebApp (RU / EN / DE / UK / ES; легко дописать).
- 🌓 **Тема Telegram** (светлая/тёмная) подхватывается автоматически.

---

## 🏗 Архитектура

```
              voice / text
                   │
            ┌──────▼───────┐
            │ Telegram Bot │  python-telegram-bot (async, long polling)
            └──────┬───────┘
        voice ─────┤
                   ▼
         Groq Whisper (STT)  ──►  текст
                   │
                   ▼
       Groq LLM (extract)  ──►  { title, datetime }
          + текущее время и таймзона пользователя
                   │
        подтверждение  ✅ / ✏️ / ❌
                   ▼
        ┌──────────────────┐      ┌──────────────┐
        │   PostgreSQL     │◄────►│ APScheduler  │──► 🔔 доставка
        │  users           │      │  restore on  │    ✅ Готово
        │  reminders       │      │  restart     │    ⏰ +1 час
        └────────┬─────────┘      └──────────────┘
                 │
          ┌──────▼───────┐
          │   FastAPI    │  initData HMAC-валидация
          │  /api/...    │
          └──────┬───────┘
                 │
          ┌──────▼───────┐
          │   WebApp     │  React + Vite + react-big-calendar
          └──────────────┘
```

**Бот и API запускаются в одном процессе** (`app/main.py`) — один сервис на
Railway. WebApp — отдельный статический сервис.

### Структура

```
bot/                     # Python: бот + API + планировщик
  app/
    config.py            # переменные окружения
    constants.py         # status/source как валидируемые строки
    db/                  # engine, модели (User, Reminder)
    services/            # stt, extract, reminders, users, scheduler, timeutils
    handlers/            # commands, messages (voice/text), callbacks
    i18n/                # локали RU/EN/DE/UK/ES
    api/                 # FastAPI: auth (initData), routes, schemas
    main.py              # запуск всего в одном процессе
  alembic/               # миграции БД
  Dockerfile
webapp/                  # React + Vite + TypeScript
  src/
    components/          # Calendar, ReminderModal, LangSwitch
    api.ts, telegram.ts, i18n.ts
  Dockerfile, nginx.conf
```

### База данных

**users**: `id`, `telegram_id` (unique), `username`, `first_name`,
`timezone` (default `Europe/Berlin`), `language`, `created_at`.

**reminders**: `id`, `user_id` (FK), `title`, `remind_at` (timestamptz),
`status` (`pending`/`done`/`cancelled`), `source` (`voice`/`text`/`manual`),
`original_text`, `created_at`, `updated_at`.

`status` и `source` хранятся **строками с валидацией в коде** (не нативный PG
enum) — миграции остаются простыми.

---

## 🔑 Получение ключей (бесплатно)

### Telegram Bot Token
1. Открой [@BotFather](https://t.me/BotFather) в Telegram.
2. `/newbot` → задай имя и username → получишь **токен** вида `123456:ABC...`.
3. (Для WebApp-кнопки) у бота уже всё готово; URL WebApp задаётся через `WEBAPP_URL`.

### Groq API Key
1. Зайди на [console.groq.com](https://console.groq.com) (бесплатный аккаунт).
2. **API Keys → Create API Key** → скопируй ключ `gsk_...`.
3. Whisper и LLM доступны на бесплатном тарифе.

---

## 💻 Локальный запуск

### 1. PostgreSQL
Подними локальную БД (например в Docker):
```bash
docker run --name reminders-db -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=reminders -p 5432:5432 -d postgres:16
```

### 2. Бот + API
```bash
cd bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # заполни TELEGRAM_BOT_TOKEN, GROQ_API_KEY, DATABASE_URL
#   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reminders

alembic upgrade head        # создать таблицы
python -m app.main          # бот (polling) + API на :8000
```
> Для голосового фолбэка нужен **ffmpeg** в PATH (на большинстве систем `.oga`
> и так принимается Groq напрямую; ffmpeg — подстраховка).

### 3. WebApp
```bash
cd webapp
npm install
cp .env.example .env         # VITE_API_URL=http://localhost:8000
npm run dev                  # http://localhost:5173
```
> WebApp авторизуется через Telegram `initData`, поэтому **полноценно работает
> только при открытии из Telegram** (кнопка «📅 Мои напоминания»). Для локальной
> отладки UI открой в браузере — список будет пустым (нет валидного initData).

### Проверить связку
1. Напиши боту `/start` — зарегистрируешься, увидишь приветствие.
2. Пришли голосовое или текст: «напомни через 2 минуты выпить воды».
3. Подтверди «✅ Сохранить» — в назначенное время придёт 🔔.

---

## 🚀 Деплой на Railway (бесплатно)

Понадобятся **3 компонента**: PostgreSQL, сервис бота, сервис WebApp.

### 1. PostgreSQL
В проекте Railway: **New → Database → PostgreSQL**. Railway создаст переменную
`DATABASE_URL` (драйвер нормализуется на `asyncpg` автоматически в `config.py`).

### 2. Сервис бота (`bot/`)
- **New → GitHub Repo** (или Empty Service) → Root Directory: `bot`.
- Сборка по `bot/Dockerfile` (внутри уже `alembic upgrade head` перед стартом).
- Переменные окружения:
  | Переменная | Значение |
  |---|---|
  | `TELEGRAM_BOT_TOKEN` | токен от BotFather |
  | `GROQ_API_KEY` | ключ Groq |
  | `DATABASE_URL` | ссылка на Postgres (Reference из БД-сервиса) |
  | `WEBAPP_URL` | публичный URL сервиса WebApp (см. шаг 3) |
- Бот работает по long polling — публичный домен ему не обязателен, но он нужен
  для API. Включи **Networking → Public Networking** и задай `API_PORT` (Railway
  обычно прокидывает `PORT`; при необходимости выставь `API_PORT=8000` и
  настрой порт в настройках сервиса).

### 3. Сервис WebApp (`webapp/`)
- **New → тот же репо** → Root Directory: `webapp`, сборка по `webapp/Dockerfile`.
- **Build-переменная** `VITE_API_URL` = публичный URL сервиса бота
  (например `https://reminder-bot.up.railway.app`).
- Включи Public Networking → получишь домен, например
  `https://reminder-webapp.up.railway.app`.

### 4. Связать
- Пропиши полученный URL WebApp в `WEBAPP_URL` сервиса бота (redeploy).
- В [@BotFather](https://t.me/BotFather): `/setdomain` (или **Bot Settings →
  Domain**) → укажи домен WebApp, чтобы Telegram разрешил открытие WebApp.

После этого кнопка «📅 Мои напоминания» в боте откроет календарь.

---

## 🌐 Добавить язык
- **Бот**: добавь словарь в `bot/app/i18n/locales.py`.
- **WebApp**: добавь объект в `STRINGS` в `webapp/src/i18n.ts`.

Английский — язык-фолбэк и источник истины по набору ключей.

---

## 🖼 Скриншоты (плейсхолдеры для портфолио)

| Голос → напоминание | Подтверждение | WebApp-календарь |
|---|---|---|
| _screenshot_ | _screenshot_ | _screenshot_ |

---

## 📋 Чеклист multi-user
- [x] Пользователь создаётся на первом контакте (`/start` или любое сообщение).
- [x] Все запросы к `reminders` фильтруются по `user_id`.
- [x] API авторизуется по подписи Telegram `initData` (нельзя действовать за
      другого пользователя).
- [x] Никаких захардкоженных Telegram ID.
- [x] Таймзона и язык — на пользователя.
