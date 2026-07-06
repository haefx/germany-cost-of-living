"""Self-service account deletion and cascade cleanup."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import ExpenseEntry, IncomeEntry
from app.models.user import User
from tests.helpers import register_and_login


async def test_deleting_account_removes_login_access(client: AsyncClient) -> None:
    await register_and_login(client, "delete-a@example.com")

    delete_response = await client.delete("/api/users/me")
    assert delete_response.status_code == 204

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "delete-a@example.com", "password": "correct-horse-battery"},
    )
    assert login_response.status_code == 400


async def test_deleting_account_cascades_finance_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await register_and_login(client, "delete-b@example.com")
    me_response = await client.get("/api/users/me")
    user_id = me_response.json()["id"]

    await client.post(
        "/api/income", json={"label": "Gehalt", "amount": "3000", "entry_date": "2026-06-01"}
    )
    await client.post(
        "/api/expenses", json={"label": "Miete", "amount": "1000", "entry_date": "2026-06-01"}
    )

    await client.delete("/api/users/me")

    remaining_user = (
        await db_session.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    assert remaining_user is None

    remaining_income = (
        (await db_session.execute(select(IncomeEntry).where(IncomeEntry.user_id == user_id)))
        .scalars()
        .all()
    )
    remaining_expenses = (
        (await db_session.execute(select(ExpenseEntry).where(ExpenseEntry.user_id == user_id)))
        .scalars()
        .all()
    )
    assert remaining_income == []
    assert remaining_expenses == []


async def test_deleting_one_account_does_not_affect_another(client: AsyncClient) -> None:
    await register_and_login(client, "delete-c@example.com")
    await client.post("/api/auth/logout")
    await register_and_login(client, "delete-d@example.com")

    await client.delete("/api/users/me")

    login_response = await client.post(
        "/api/auth/login",
        data={"username": "delete-c@example.com", "password": "correct-horse-battery"},
    )
    assert login_response.status_code == 204
