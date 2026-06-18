"""APScheduler wrapper that delivers reminders via the Telegram bot.

Design
------
* A single ``AsyncIOScheduler`` runs in the bot's event loop.
* On reminder creation we add a one-shot ``DateTrigger`` job.
* On startup ``restore()`` re-reads every pending future reminder from the DB
  and re-arms the jobs — so a restart/redeploy never loses a reminder.
* When a job fires we re-check the DB (the reminder may have been done/cancelled
  or rescheduled in the meantime) and only then notify the user.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from app.constants import STATUS_PENDING
from app.db.base import SessionLocal
from app.i18n import t
from app.services import reminders as reminders_repo

logger = logging.getLogger(__name__)


def _job_id(reminder_id: int) -> str:
    return f"reminder:{reminder_id}"


class ReminderScheduler:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._bot: Bot | None = None

    def start(self, bot: Bot) -> None:
        self._bot = bot
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    # --- scheduling API ---------------------------------------------------

    def schedule(self, reminder_id: int, remind_at: datetime) -> None:
        """Arm (or re-arm) a one-shot job for the given reminder."""
        run_date = remind_at
        if run_date.tzinfo is None:
            run_date = run_date.replace(tzinfo=timezone.utc)
        # If the time is already in the past (e.g. restored late), fire ASAP.
        now = datetime.now(timezone.utc)
        if run_date < now:
            run_date = now + timedelta(seconds=1)
        self._scheduler.add_job(
            self._fire,
            trigger=DateTrigger(run_date=run_date),
            args=[reminder_id],
            id=_job_id(reminder_id),
            replace_existing=True,
            misfire_grace_time=3600,  # tolerate downtime up to 1h
        )

    def cancel(self, reminder_id: int) -> None:
        try:
            self._scheduler.remove_job(_job_id(reminder_id))
        except Exception:  # noqa: BLE001 - job may not exist; that's fine
            pass

    async def restore(self) -> None:
        """Re-arm jobs for all pending future reminders after a restart."""
        async with SessionLocal() as session:
            pending = await reminders_repo.list_pending_future_all(session)
        for r in pending:
            self.schedule(r.id, r.remind_at)
        logger.info("Restored %d reminder job(s)", len(pending))

    # --- delivery ---------------------------------------------------------

    async def _fire(self, reminder_id: int) -> None:
        if self._bot is None:
            logger.error("Scheduler has no bot; cannot deliver %s", reminder_id)
            return
        async with SessionLocal() as session:
            # Re-fetch without user scoping (system job) then load the user.
            from sqlalchemy import select  # local import to avoid cycle

            from app.db.models import Reminder

            reminder = (
                await session.execute(
                    select(Reminder).where(Reminder.id == reminder_id)
                )
            ).scalar_one_or_none()

            if reminder is None or reminder.status != STATUS_PENDING:
                return  # done/cancelled/deleted in the meantime

            # Load owner to get chat id + language + timezone.
            from app.db.models import User

            owner = (
                await session.execute(
                    select(User).where(User.id == reminder.user_id)
                )
            ).scalar_one_or_none()
            if owner is None:
                return

            lang = owner.language
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            t("btn_done", lang), callback_data=f"done:{reminder.id}"
                        ),
                        InlineKeyboardButton(
                            t("btn_snooze", lang),
                            callback_data=f"snooze:{reminder.id}",
                        ),
                    ]
                ]
            )
            text = t("reminder_fire", lang, title=reminder.title)

        try:
            await self._bot.send_message(
                chat_id=owner.telegram_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as exc:  # noqa: BLE001 - never crash the scheduler
            logger.warning("Failed to deliver reminder %s: %s", reminder_id, exc)


# Process-wide singleton used by handlers and the API.
scheduler = ReminderScheduler()
