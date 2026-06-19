"""Shared handler helpers."""
from __future__ import annotations

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from app.config import settings
from app.i18n import t


def webapp_inline(lang: str | None) -> InlineKeyboardMarkup | None:
    """Inline button that opens the WebApp.

    Inline web_app buttons deliver a valid Telegram ``initData`` (unlike
    reply-keyboard web_app buttons, which delivered an empty initData → 401),
    so this is the WebApp entry point while the blue menu button stays on the
    command list. Returns None if WEBAPP_URL isn't a valid https URL.
    """
    if not settings.webapp_url_is_https:
        return None
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("btn_webapp", lang),
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
    )


def confirm_keyboard(lang: str | None) -> InlineKeyboardMarkup:
    """Save / Edit / Cancel buttons shown after parsing a reminder."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t("btn_save", lang), callback_data="save"),
                InlineKeyboardButton(t("btn_edit", lang), callback_data="edit"),
                InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel"),
            ]
        ]
    )
