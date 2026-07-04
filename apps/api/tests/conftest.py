"""Shared pytest fixtures for the API test suite.

Tests run against a real Postgres database (not SQLite), migrated with the
project's actual Alembic migrations, because Alembic targets Postgres
specifically and a stand-in SQLite schema could hide real drift between the
models and the migrations. Each test gets its own outer transaction that is
rolled back afterwards (via ``join_transaction_mode="create_savepoint"``, so
the application code's own commits become savepoints rather than ending the
test's transaction) — this is what gives every test full isolation without
needing to truncate tables between them.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://gcol:gcol@localhost:55432/gcol_test"
)
API_ROOT = Path(__file__).resolve().parents[1]

# NullPool: pytest-asyncio uses a fresh event loop per test function by
# default, and asyncpg connections cannot be reused across event loops. A
# pooled connection handed out in one test's loop would break in the next.
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


def _apply_migrations() -> None:
    async def _reset_schema() -> None:
        async with engine.begin() as conn:
            await conn.exec_driver_sql("DROP SCHEMA public CASCADE")
            await conn.exec_driver_sql("CREATE SCHEMA public")

    asyncio.run(_reset_schema())

    cfg = Config(str(API_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def _migrated_database() -> None:
    _apply_migrations()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    outer_transaction = await connection.begin()
    session_factory = async_sessionmaker(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )
    session = session_factory()

    yield session

    await session.close()
    await outer_transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from app.db import get_session
    from app.main import app

    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
