"""Inline-button callback handler.

Two groups of buttons:
* Confirmation card: ``save`` / ``edit`` / ``cancel``
* Fired reminder:    ``done:<id>`` / ``snooze:<id>``
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.constants import SOURCE_MANUAL  # noqa: F401  (kept for clarity)
from app.db.base import SessionLocal
from app.i18n import normalize_lang, t
from app.services import reminders as reminders_repo
from app.services import users as users_repo
from app.services.scheduler import scheduler
from app.services.timeutils import format_local

logger = logging.getLogger(__name__)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    data = query.data or ""
    tg_user = update.effective_user
    assert tg_user is not None

    if data in {"save", "edit", "cancel"}:
        await _handle_confirm(update, context, data)
    elif data.startswith("done:"):
        await _handle_done(update, int(data.split(":", 1)[1]))
    elif data.startswith("snooze:"):
        await _handle_snooze(update, int(data.split(":", 1)[1]))


async def _handle_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE, action: str
) -> None:
    query = update.callback_query
    tg_user = update.effective_user
    pending = context.user_data.get("pending")
    lang = (pending or {}).get("lang") or normalize_lang(tg_user.language_code)

    if action == "cancel":
        context.user_data.pop("pending", None)
        await query.edit_message_text(t("cancelled", lang))
        return

    if action == "edit":
        context.user_data.pop("pending", None)
        await query.edit_message_text(t("edit_prompt", lang))
        return

    # action == "save"
    if not pending:
        await query.edit_message_text(t("expired", lang))
        return

    async with SessionLocal() as session:
        user = await users_repo.get_by_telegram_id(session, tg_user.id)
        if user is None:
            await query.edit_message_text(t("err_generic", lang))
            return
        reminder = await reminders_repo.create(
            session,
            user_id=user.id,
            title=pending["title"],
            remind_at=pending["remind_at_utc"],
            source=pending["source"],
            original_text=pending.get("original_text"),
        )
        tz = user.timezone

    # Arm the scheduler job.
    scheduler.schedule(reminder.id, reminder.remind_at)
    context.user_data.pop("pending", None)

    when = format_local(reminder.remind_at, tz)
    await query.edit_message_text(
        t("saved_ok", lang, when=when), parse_mode=ParseMode.MARKDOWN
    )


async def _handle_done(update: Update, reminder_id: int) -> None:
    query = update.callback_query
    tg_user = update.effective_user
    async with SessionLocal() as session:
        user = await users_repo.get_by_telegram_id(session, tg_user.id)
        if user is None:
            return
        lang = user.language
        await reminders_repo.mark_done(
            session, user_id=user.id, reminder_id=reminder_id
        )
    scheduler.cancel(reminder_id)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(t("done_ok", lang))


async def _handle_snooze(update: Update, reminder_id: int) -> None:
    query = update.callback_query
    tg_user = update.effective_user
    new_time = datetime.now(timezone.utc) + timedelta(hours=1)
    async with SessionLocal() as session:
        user = await users_repo.get_by_telegram_id(session, tg_user.id)
        if user is None:
            return
        lang = user.language
        updated = await reminders_repo.update(
            session,
            user_id=user.id,
            reminder_id=reminder_id,
            remind_at=new_time,
            status="pending",
        )
        tz = user.timezone

    if updated is None:
        await query.message.reply_text(t("expired", lang))
        return

    scheduler.schedule(reminder_id, new_time)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        t("snoozed_ok", lang, when=format_local(new_time, tz)),
        parse_mode=ParseMode.MARKDOWN,
    )
