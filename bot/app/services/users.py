"""User repository: registration and settings updates.

Multi-user by design — a user is identified by their Telegram id and created
on first contact (/start or any message). Nothing is hardcoded to one id.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User


async def get_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_or_create(
    session: AsyncSession,
    *,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    language: str | None = None,
) -> tuple[User, bool]:
    """Return (user, created). Registers the user on first contact."""
    user = await get_by_telegram_id(session, telegram_id)
    if user is not None:
        # Keep lightweight profile fields fresh.
        changed = False
        if username and user.username != username:
            user.username, changed = username, True
        if first_name and user.first_name != first_name:
            user.first_name, changed = first_name, True
        if language and not user.language:
            user.language, changed = language, True
        if changed:
            await session.commit()
        return user, False

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        language=language,
        timezone=settings.default_timezone,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user, True


async def set_timezone(session: AsyncSession, user: User, tz: str) -> None:
    user.timezone = tz
    await session.commit()


async def set_language(session: AsyncSession, user: User, lang: str) -> None:
    user.language = lang
    await session.commit()
