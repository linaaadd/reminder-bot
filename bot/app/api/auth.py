"""Telegram WebApp ``initData`` validation.

The WebApp frontend sends the raw ``initData`` string (from
``window.Telegram.WebApp.initData``) in the ``X-Telegram-Init-Data`` header.
We verify the HMAC signature with the bot token so a user can only ever act as
themselves — this is what makes the API multi-user-safe.

Spec: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException, status

from app.config import settings

# Reject initData older than this (replay protection). 24h is generous.
_MAX_AUTH_AGE_SECONDS = 24 * 60 * 60


@dataclass
class TelegramAuth:
    telegram_id: int
    username: str | None
    first_name: str | None
    language_code: str | None


def _check_signature(init_data: str) -> dict[str, str]:
    """Return the parsed fields if the signature is valid, else raise."""
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing hash")

    # data_check_string: keys sorted, "key=value" joined by newlines.
    data_check_string = "\n".join(
        f"{k}={pairs[k]}" for k in sorted(pairs.keys())
    )
    secret_key = hmac.new(
        b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad signature")

    # Replay protection via auth_date.
    auth_date = int(pairs.get("auth_date", "0"))
    if auth_date and (time.time() - auth_date) > _MAX_AUTH_AGE_SECONDS:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData expired")

    return pairs


async def require_telegram_auth(
    x_telegram_init_data: str = Header(default=""),
) -> TelegramAuth:
    """FastAPI dependency: validate initData and return the Telegram user."""
    if not x_telegram_init_data:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "missing X-Telegram-Init-Data"
        )
    pairs = _check_signature(x_telegram_init_data)

    user_json = pairs.get("user")
    if not user_json:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "no user in initData")
    try:
        user = json.loads(user_json)
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad user payload")

    return TelegramAuth(
        telegram_id=int(user["id"]),
        username=user.get("username"),
        first_name=user.get("first_name"),
        language_code=user.get("language_code"),
    )
