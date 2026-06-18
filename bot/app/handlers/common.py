"""Shared handler helpers."""
from __future__ import annotations

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from app.config import settings
from app.i18n import t


def webapp_keyboard(lang: str | None) -> ReplyKeyboardMarkup | None:
    """Persistent reply keyboard with the WebApp button (if WEBAPP_URL is set)."""
    if not settings.webapp_url_is_https:
        return None
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t("btn_webapp", lang), web_app=WebAppInfo(url=settings.webapp_url))]],
        resize_keyboard=True,
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
