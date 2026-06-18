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
from telegram.ext import Application, ApplicationBuilder

from app.api.server import create_api
from app.config import settings
from app.handlers import register
from app.services.scheduler import scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("reminder-bot")


async def _run() -> None:
    # Build and start the Telegram application.
    application: Application = (
        ApplicationBuilder().token(settings.telegram_bot_token).build()
    )
    register(application)

    await application.initialize()
    await application.start()

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
