"""Handler registration."""
from __future__ import annotations

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.handlers import callbacks, commands, messages


def register(app: Application) -> None:
    # Commands
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_cmd))
    app.add_handler(CommandHandler("list", commands.list_cmd))
    app.add_handler(CommandHandler("app", commands.app_cmd))
    app.add_handler(CommandHandler("timezone", commands.timezone_cmd))

    # Inline button callbacks (save/edit/cancel/done/snooze)
    app.add_handler(CallbackQueryHandler(callbacks.on_callback))

    # Voice + text reminders (text excludes commands)
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, messages.on_voice))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, messages.on_text)
    )
