"""initial schema: users, reminders

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_users_telegram_id", "users", ["telegram_id"], unique=True
    )

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("original_text", sa.String(length=4096), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])
    op.create_index(
        "ix_reminders_user_remind_at", "reminders", ["user_id", "remind_at"]
    )
    op.create_index(
        "ix_reminders_status_remind_at", "reminders", ["status", "remind_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_reminders_status_remind_at", table_name="reminders")
    op.drop_index("ix_reminders_user_remind_at", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_table("reminders")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
