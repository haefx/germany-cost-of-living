"""Demo-household provisioning and expiry."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import ExpenseEntry, IncomeEntry
from app.models.user import User
from app.services.demo_service import expire_demo_users, provision_demo_user


async def test_starting_a_demo_session_logs_in_immediately(client: AsyncClient) -> None:
    response = await client.post("/api/demo/start")
    assert response.status_code == 204
    assert "gcol_session_v2" in response.cookies

    me_response = await client.get("/api/users/me")
    assert me_response.status_code == 200
    body = me_response.json()
    assert body["is_demo"] is True
    assert body["demo_expires_at"] is not None


async def test_demo_session_has_seeded_household_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await client.post("/api/demo/start")
    me_response = await client.get("/api/users/me")
    user_id = me_response.json()["id"]

    income_result = await db_session.execute(
        select(IncomeEntry).where(IncomeEntry.user_id == user_id)
    )
    expense_result = await db_session.execute(
        select(ExpenseEntry).where(ExpenseEntry.user_id == user_id)
    )
    assert len(income_result.scalars().all()) >= 1
    assert len(expense_result.scalars().all()) >= 1


async def test_expire_demo_users_removes_only_expired_demo_accounts(
    db_session: AsyncSession,
) -> None:
    now = datetime.now(UTC)

    expired_demo = await provision_demo_user(db_session)
    expired_demo.demo_expires_at = now - timedelta(hours=1)

    active_demo = await provision_demo_user(db_session)
    active_demo.demo_expires_at = now + timedelta(hours=1)

    await db_session.flush()

    deleted_count = await expire_demo_users(db_session)
    await db_session.flush()

    assert deleted_count == 1

    remaining_ids = (await db_session.execute(select(User.id))).scalars().all()
    assert expired_demo.id not in remaining_ids
    assert active_demo.id in remaining_ids


async def test_expiring_demo_users_cascades_their_finance_data(
    db_session: AsyncSession,
) -> None:
    demo_user = await provision_demo_user(db_session)
    demo_user.demo_expires_at = datetime.now(UTC) - timedelta(hours=1)
    await db_session.flush()

    await expire_demo_users(db_session)
    await db_session.flush()

    remaining = await db_session.execute(
        select(IncomeEntry).where(IncomeEntry.user_id == demo_user.id)
    )
    assert remaining.scalars().all() == []


async def test_expire_demo_users_never_touches_real_accounts(
    db_session: AsyncSession,
) -> None:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    from app.security.password import password_helper

    user_db = SQLAlchemyUserDatabase(db_session, User)
    real_user = await user_db.create(
        {
            "email": "real-user@example.com",
            "hashed_password": password_helper.hash("some-password"),
            "is_active": True,
            "is_demo": False,
        }
    )

    deleted_count = await expire_demo_users(db_session)

    assert deleted_count == 0
    remaining_ids = (await db_session.execute(select(User.id))).scalars().all()
    assert real_user.id in remaining_ids
