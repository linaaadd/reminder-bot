"""Reminder repository: all CRUD, always scoped to a user_id.

Every function takes ``user_id`` and filters by it so a user can only ever
touch their own rows — this is the core multi-user guarantee.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import (
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_PENDING,
    capitalize_first,
    validate_source,
    validate_status,
)
from app.db.models import Reminder


async def create(
    session: AsyncSession,
    *,
    user_id: int,
    title: str,
    remind_at: datetime,
    source: str,
    original_text: str | None = None,
) -> Reminder:
    validate_source(source)
    reminder = Reminder(
        user_id=user_id,
        title=capitalize_first(title),
        remind_at=remind_at,
        source=source,
        original_text=original_text,
        status=STATUS_PENDING,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def get(
    session: AsyncSession, *, user_id: int, reminder_id: int
) -> Reminder | None:
    result = await session.execute(
        select(Reminder).where(
            Reminder.id == reminder_id, Reminder.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def list_for_user(
    session: AsyncSession,
    *,
    user_id: int,
    only_pending: bool = False,
    upcoming_only: bool = False,
    limit: int | None = None,
) -> list[Reminder]:
    stmt = select(Reminder).where(Reminder.user_id == user_id)
    if only_pending:
        stmt = stmt.where(Reminder.status == STATUS_PENDING)
    if upcoming_only:
        stmt = stmt.where(Reminder.remind_at >= datetime.now(timezone.utc))
    stmt = stmt.order_by(Reminder.remind_at.asc())
    if limit:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_pending_future_all(session: AsyncSession) -> list[Reminder]:
    """All pending reminders in the future — used to restore the scheduler."""
    result = await session.execute(
        select(Reminder).where(
            Reminder.status == STATUS_PENDING,
            Reminder.remind_at >= datetime.now(timezone.utc),
        )
    )
    return list(result.scalars().all())


async def update(
    session: AsyncSession,
    *,
    user_id: int,
    reminder_id: int,
    title: str | None = None,
    remind_at: datetime | None = None,
    status: str | None = None,
) -> Reminder | None:
    reminder = await get(session, user_id=user_id, reminder_id=reminder_id)
    if reminder is None:
        return None
    if title is not None:
        reminder.title = capitalize_first(title)
    if remind_at is not None:
        reminder.remind_at = remind_at
    if status is not None:
        reminder.status = validate_status(status)
    await session.commit()
    await session.refresh(reminder)
    return reminder


async def mark_done(
    session: AsyncSession, *, user_id: int, reminder_id: int
) -> Reminder | None:
    return await update(
        session, user_id=user_id, reminder_id=reminder_id, status=STATUS_DONE
    )


async def cancel(
    session: AsyncSession, *, user_id: int, reminder_id: int
) -> Reminder | None:
    return await update(
        session,
        user_id=user_id,
        reminder_id=reminder_id,
        status=STATUS_CANCELLED,
    )


async def delete(
    session: AsyncSession, *, user_id: int, reminder_id: int
) -> bool:
    reminder = await get(session, user_id=user_id, reminder_id=reminder_id)
    if reminder is None:
        return False
    await session.delete(reminder)
    await session.commit()
    return True
