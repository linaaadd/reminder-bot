"""Entry point: runs the Telegram bot, scheduler and FastAPI in ONE process.

Everything shares a single asyncio event loop:
    * python-telegram-bot  — long polling
    * APScheduler          — fires reminder jobs
    * FastAPI (uvicorn)    — serves the WebApp API

This is the single Railway service the project targets.
"""
from __future__ import annotations

import asyncio
import logging
import sys

import uvicorn
from telegram import (
    BotCommand,
    MenuButtonCommands,
    MenuButtonWebApp,
    WebAppInfo,
)
from telegram.ext import Application, ApplicationBuilder

from app.api.server import create_api
from app.config import settings
from app.handlers import register
from app.i18n import SUPPORTED, t
from app.services.scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("reminder-bot")


# Short command descriptions for the Telegram "/" menu, per language.
# Falls back to English for any language not listed here.
_CMD_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "en": {
        "start": "Start / how it works",
        "list": "My upcoming reminders",
        "timezone": "Set my timezone",
        "help": "Help",
    },
    "ru": {
        "start": "Старт / как это работает",
        "list": "Мои ближайшие напоминания",
        "timezone": "Установить часовой пояс",
        "help": "Помощь",
    },
    "de": {
        "start": "Start / wie es funktioniert",
        "list": "Kommende Erinnerungen",
        "timezone": "Zeitzone einstellen",
        "help": "Hilfe",
    },
    "uk": {
        "start": "Старт / як це працює",
        "list": "Найближчі нагадування",
        "timezone": "Встановити часовий пояс",
        "help": "Допомога",
    },
    "es": {
        "start": "Inicio / cómo funciona",
        "list": "Próximos recordatorios",
        "timezone": "Configurar zona horaria",
        "help": "Ayuda",
    },
}


async def _setup_bot_menu(application: Application) -> None:
    """Register the command list and the WebApp menu button (one-time on boot).

    * setMyCommands → populates the blue "/" command menu (per language).
    * setChatMenuButton → makes the menu button open the WebApp directly,
      so users have an obvious way in (only if WEBAPP_URL is configured).
    """
    bot = application.bot
    order = ("start", "list", "timezone", "help")

    # English default + one set per supported language.
    en = _CMD_DESCRIPTIONS["en"]
    await bot.set_my_commands([BotCommand(c, en[c]) for c in order])
    for lang in SUPPORTED:
        desc = _CMD_DESCRIPTIONS.get(lang, en)
        await bot.set_my_commands(
            [BotCommand(c, desc[c]) for c in order], language_code=lang
        )

    # Menu button: open the WebApp if we have a valid https URL, else commands.
    try:
        if settings.webapp_url_is_https:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text=t("btn_webapp", "en"),
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            )
            logger.info("WebApp menu button set -> %s", settings.webapp_url)
        else:
            await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
            logger.warning(
                "WEBAPP_URL missing/invalid (%r); WebApp button unavailable",
                settings.webapp_url,
            )
    except Exception as exc:  # noqa: BLE001 - never let menu setup crash the bot
        logger.warning("Could not set chat menu button: %s", exc)


async def _run() -> None:
    # Build and start the Telegram application.
    application: Application = (
        ApplicationBuilder().token(settings.telegram_bot_token).build()
    )
    register(application)

    await application.initialize()
    await application.start()

    # Register the "/" command menu and the WebApp menu button.
    # Belt-and-suspenders: menu setup must never take down the bot.
    try:
        await _setup_bot_menu(application)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Bot menu setup failed (continuing): %s", exc)

    # Scheduler needs the bot to deliver messages; restore jobs after a restart.
    scheduler.start(application.bot)
    await scheduler.restore()

    await application.updater.start_polling(drop_pending_updates=False)
    logger.info("Bot polling started")

    # Start the FastAPI server in the same loop.
    api = create_api()
    config = uvicorn.Config(
        api,
        host=settings.api_host,
        port=settings.api_port,
        loop="asyncio",
        log_level="info",
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()  # blocks until the server is told to stop
    finally:
        logger.info("Shutting down...")
        scheduler.shutdown()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main() -> None:
    # asyncpg + Windows need the selector loop policy for local development.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(_run())


if __name__ == "__main__":
    main()
