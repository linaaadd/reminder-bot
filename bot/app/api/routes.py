"""WebApp CRUD endpoints. Every route is scoped to the authenticated user."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import TelegramAuth, require_telegram_auth
from app.api.schemas import (
    ReminderCreate,
    ReminderOut,
    ReminderUpdate,
    UserOut,
)
from app.constants import SOURCE_MANUAL
from app.db.base import get_session
from app.db.models import User
from app.i18n import normalize_lang
from app.services import reminders as reminders_repo
from app.services import users as users_repo
from app.services.scheduler import scheduler
from app.services.timeutils import local_naive_to_utc

router = APIRouter(prefix="/api", tags=["reminders"])


async def _current_user(
    auth: TelegramAuth = Depends(require_telegram_auth),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolve (and lazily register) the authenticated Telegram user."""
    user, _ = await users_repo.get_or_create(
        session,
        telegram_id=auth.telegram_id,
        username=auth.username,
        first_name=auth.first_name,
        language=normalize_lang(auth.language_code),
    )
    return user


def _to_utc(dt: datetime, tz: str) -> datetime:
    """Normalize an incoming datetime to a tz-aware UTC instant."""
    if dt.tzinfo is None:
        # Naive → interpret in the user's timezone.
        return local_naive_to_utc(dt, tz)
    return dt.astimezone(timezone.utc)


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(_current_user)) -> User:
    return user


@router.get("/reminders", response_model=list[ReminderOut])
async def list_reminders(
    user: User = Depends(_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await reminders_repo.list_for_user(session, user_id=user.id)


@router.post(
    "/reminders", response_model=ReminderOut, status_code=status.HTTP_201_CREATED
)
async def create_reminder(
    payload: ReminderCreate,
    user: User = Depends(_current_user),
    session: AsyncSession = Depends(get_session),
):
    remind_at = _to_utc(payload.remind_at, user.timezone)
    reminder = await reminders_repo.create(
        session,
        user_id=user.id,
        title=payload.title,
        remind_at=remind_at,
        source=SOURCE_MANUAL,
    )
    scheduler.schedule(reminder.id, reminder.remind_at)
    return reminder


@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
async def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    user: User = Depends(_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        new_status = payload.validated_status()
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "invalid status")

    remind_at = (
        _to_utc(payload.remind_at, user.timezone)
        if payload.remind_at is not None
        else None
    )
    updated = await reminders_repo.update(
        session,
        user_id=user.id,
        reminder_id=reminder_id,
        title=payload.title,
        remind_at=remind_at,
        status=new_status,
    )
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "reminder not found")

    # Re-arm or drop the scheduler job depending on the new state.
    if updated.status == "pending":
        scheduler.schedule(updated.id, updated.remind_at)
    else:
        scheduler.cancel(updated.id)
    return updated


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    user: User = Depends(_current_user),
    session: AsyncSession = Depends(get_session),
):
    ok = await reminders_repo.delete(
        session, user_id=user.id, reminder_id=reminder_id
    )
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "reminder not found")
    scheduler.cancel(reminder_id)
