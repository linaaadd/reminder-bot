"""ORM models: User and Reminder.

Notes
-----
* ``status`` / ``source`` are stored as plain strings (not a native PG enum)
  and validated in the application layer — see ``constants.py``. This keeps
  migrations painless: adding a new value never requires an ALTER TYPE.
* Everything is multi-user: a reminder always belongs to exactly one user via
  ``user_id`` and every query filters by it.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    # IANA tz name, e.g. "Europe/Berlin". Default set from settings on create.
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str | None] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    # Stored as timestamptz (UTC instant); rendered in the user's tz on display.
    remind_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default="pending", nullable=False
    )  # pending | done | cancelled
    source: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # voice | text | manual
    original_text: Mapped[str | None] = mapped_column(String(4096))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="reminders")

    __table_args__ = (
        # Fast "my upcoming reminders" listing.
        Index("ix_reminders_user_remind_at", "user_id", "remind_at"),
        # Fast scheduler restore: pull all pending future reminders.
        Index("ix_reminders_status_remind_at", "status", "remind_at"),
    )
