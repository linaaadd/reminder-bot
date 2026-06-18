"""Pydantic request/response schemas for the WebApp API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import STATUSES


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    remind_at: datetime  # tz-aware UTC instant
    status: str
    source: str
    created_at: datetime


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=1024)
    # Absolute instant. Frontend should send ISO 8601 with offset/Z.
    remind_at: datetime


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=1024)
    remind_at: datetime | None = None
    status: str | None = None

    def validated_status(self) -> str | None:
        if self.status is not None and self.status not in STATUSES:
            raise ValueError("invalid status")
        return self.status


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    first_name: str | None
    timezone: str
    language: str | None
