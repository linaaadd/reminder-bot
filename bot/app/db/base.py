"""Async SQLAlchemy engine, session factory and declarative base."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


# Single shared engine for the whole process.
engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,  # survive idle disconnects on free-tier Postgres
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield a session, always close it."""
    async with SessionLocal() as session:
        yield session
