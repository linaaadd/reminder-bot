"""Command handlers: /start /help /list /timezone."""
from __future__ import annotations

import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.db.base import SessionLocal
from app.handlers.common import webapp_inline
from app.i18n import normalize_lang, t
from app.services import reminders as reminders_repo
from app.services import users as users_repo
from app.services.timeutils import format_local, is_valid_timezone

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    assert tg_user is not None
    lang = normalize_lang(tg_user.language_code)

    async with SessionLocal() as session:
        user, created = await users_repo.get_or_create(
            session,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=lang,
        )
        tz = user.timezone

    # Greeting carries the inline WebApp button (delivers a valid initData).
    # reply_markup is the inline button if WEBAPP_URL is set, else clear any
    # legacy reply keyboard from older versions.
    await update.message.reply_text(
        t("start_greeting", lang, name=tg_user.first_name or ""),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=webapp_inline(lang) or ReplyKeyboardRemove(),
    )
    # On first contact, gently nudge about the timezone.
    if created:
        await update.message.reply_text(
            t("start_tz_hint", lang, tz=tz), parse_mode=ParseMode.MARKDOWN
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = await _lang_for(update)
    await update.message.reply_text(
        t("help", lang), parse_mode=ParseMode.MARKDOWN
    )


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    assert tg_user is not None
    async with SessionLocal() as session:
        user, _ = await users_repo.get_or_create(
            session,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=normalize_lang(tg_user.language_code),
        )
        lang = user.language
        items = await reminders_repo.list_for_user(
            session,
            user_id=user.id,
            only_pending=True,
            upcoming_only=True,
            limit=20,
        )
        tz = user.timezone

    if not items:
        await update.message.reply_text(
            t("list_empty", lang), reply_markup=webapp_inline(lang)
        )
        return

    lines = [t("list_header", lang)]
    for r in items:
        lines.append(
            t("list_item", lang, title=r.title, when=format_local(r.remind_at, tz))
        )
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=webapp_inline(lang),
    )


async def app_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the WebApp calendar via an inline button."""
    lang = await _lang_for(update)
    markup = webapp_inline(lang)
    if markup is None:
        await update.message.reply_text(t("err_generic", lang))
        return
    await update.message.reply_text(t("btn_webapp", lang), reply_markup=markup)


async def timezone_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    assert tg_user is not None
    arg = " ".join(context.args).strip() if context.args else ""

    async with SessionLocal() as session:
        user, _ = await users_repo.get_or_create(
            session,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=normalize_lang(tg_user.language_code),
        )
        lang = user.language

        if not arg:
            # Show current tz + usage hint.
            await update.message.reply_text(
                t("tz_current", lang, tz=user.timezone) + "\n\n" + t("tz_usage", lang),
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if not is_valid_timezone(arg):
            await update.message.reply_text(
                t("tz_invalid", lang), parse_mode=ParseMode.MARKDOWN
            )
            return

        await users_repo.set_timezone(session, user, arg)

    await update.message.reply_text(
        t("tz_set_ok", lang, tz=arg), parse_mode=ParseMode.MARKDOWN
    )


async def _lang_for(update: Update) -> str:
    """Resolve the user's stored language (fallback to Telegram code)."""
    tg_user = update.effective_user
    if tg_user is None:
        return "en"
    async with SessionLocal() as session:
        user = await users_repo.get_by_telegram_id(session, tg_user.id)
        if user and user.language:
            return user.language
    return normalize_lang(tg_user.language_code)
