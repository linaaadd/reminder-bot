"""Message handlers: voice and text → LLM extraction → confirmation."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from app.constants import SOURCE_TEXT, SOURCE_VOICE
from app.db.base import SessionLocal
from app.handlers.common import confirm_keyboard
from app.i18n import normalize_lang, t
from app.services import users as users_repo
from app.services.extract import extract
from app.services.stt import transcribe
from app.services.timeutils import format_local

logger = logging.getLogger(__name__)


async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Voice/audio → Whisper transcription → reminder flow."""
    tg_user = update.effective_user
    assert tg_user is not None and update.message is not None
    lang = await _ensure_user_lang(tg_user)

    await update.message.chat.send_action(ChatAction.TYPING)

    voice = update.message.voice or update.message.audio
    try:
        tg_file = await context.bot.get_file(voice.file_id)
        audio_bytes = bytes(await tg_file.download_as_bytearray())
        text = await transcribe(audio_bytes, filename="voice.ogg")
    except Exception as exc:  # noqa: BLE001
        logger.exception("STT failed: %s", exc)
        await update.message.reply_text(t("err_stt", lang))
        return

    if not text:
        await update.message.reply_text(t("err_stt", lang))
        return

    # Echo what we heard (transparency + debugging aid).
    await update.message.reply_text(
        t("recognized", lang, text=text), parse_mode=ParseMode.MARKDOWN
    )
    await _process(update, context, text=text, source=SOURCE_VOICE)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Plain text → reminder flow (same pipeline as voice)."""
    tg_user = update.effective_user
    assert tg_user is not None and update.message is not None
    text = (update.message.text or "").strip()
    if not text:
        return
    await _process(update, context, text=text, source=SOURCE_TEXT)


async def _process(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    text: str,
    source: str,
) -> None:
    """Run extraction, then either ask for clarification or show a confirm card."""
    tg_user = update.effective_user
    assert tg_user is not None and update.message is not None

    async with SessionLocal() as session:
        user, _ = await users_repo.get_or_create(
            session,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=normalize_lang(tg_user.language_code),
        )
        tz = user.timezone
        stored_lang = user.language

    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        result = await extract(text, tz=tz)
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM extraction failed: %s", exc)
        await update.message.reply_text(t("err_llm", stored_lang))
        return

    # Reply in the language the user actually used (fall back to stored).
    lang = normalize_lang(result.reply_language) if result.reply_language else stored_lang

    if result.needs_clarification or result.remind_at_utc is None or not result.title:
        if result.message:
            await update.message.reply_text(
                t("needs_time", lang, message=result.message)
            )
        else:
            await update.message.reply_text(t("needs_time_generic", lang))
        return

    # Stash the pending reminder in user_data until the user confirms.
    context.user_data["pending"] = {
        "title": result.title,
        "remind_at_utc": result.remind_at_utc,
        "source": source,
        "original_text": text,
        "lang": lang,
    }

    when = format_local(result.remind_at_utc, tz)
    await update.message.reply_text(
        t("confirm", lang, title=result.title, when=when),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=confirm_keyboard(lang),
    )


async def _ensure_user_lang(tg_user) -> str:
    """Register the user if needed and return their reply language."""
    async with SessionLocal() as session:
        user, _ = await users_repo.get_or_create(
            session,
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=normalize_lang(tg_user.language_code),
        )
        return user.language or normalize_lang(tg_user.language_code)
