"""Expense entry CRUD, validation, and the uncategorized-expense case."""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import category_id_by_name, register_and_login


async def test_create_and_list_expense_entry(client: AsyncClient) -> None:
    await register_and_login(client, "expense-a@example.com")
    category_id = await category_id_by_name(client, "Lebensmittel")

    create_response = await client.post(
        "/api/expenses",
        json={
            "label": "Wocheneinkauf",
            "amount": "85.30",
            "entry_date": "2026-06-05",
            "category_id": category_id,
            "merchant": "Supermarkt",
        },
    )
    assert create_response.status_code == 201, create_response.text
    body = create_response.json()
    assert body["merchant"] == "Supermarkt"

    list_response = await client.get("/api/expenses")
    assert any(entry["id"] == body["id"] for entry in list_response.json())


async def test_expense_without_category_is_allowed(client: AsyncClient) -> None:
    await register_and_login(client, "expense-b@example.com")
    response = await client.post(
        "/api/expenses",
        json={"label": "Unbekannt", "amount": "12.50", "entry_date": "2026-06-05"},
    )
    assert response.status_code == 201
    assert response.json()["category_id"] is None


async def test_negative_amount_is_rejected(client: AsyncClient) -> None:
    await register_and_login(client, "expense-c@example.com")
    response = await client.post(
        "/api/expenses",
        json={"label": "Invalid", "amount": "-5", "entry_date": "2026-06-05"},
    )
    assert response.status_code == 422


async def test_update_expense_entry(client: AsyncClient) -> None:
    await register_and_login(client, "expense-d@example.com")
    create_response = await client.post(
        "/api/expenses", json={"label": "Kino", "amount": "20", "entry_date": "2026-06-05"}
    )
    entry_id = create_response.json()["id"]

    update_response = await client.patch(f"/api/expenses/{entry_id}", json={"is_planned": True})
    assert update_response.status_code == 200
    assert update_response.json()["is_planned"] is True


async def test_delete_expense_entry(client: AsyncClient) -> None:
    await register_and_login(client, "expense-e@example.com")
    create_response = await client.post(
        "/api/expenses", json={"label": "Kino", "amount": "20", "entry_date": "2026-06-05"}
    )
    entry_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/expenses/{entry_id}")
    assert delete_response.status_code == 204

    list_response = await client.get("/api/expenses")
    assert all(entry["id"] != entry_id for entry in list_response.json())


async def test_updating_someone_elses_expense_returns_404(client: AsyncClient) -> None:
    await register_and_login(client, "expense-f@example.com")
    create_response = await client.post(
        "/api/expenses", json={"label": "Privat", "amount": "20", "entry_date": "2026-06-05"}
    )
    entry_id = create_response.json()["id"]

    await client.post("/api/auth/logout")
    await register_and_login(client, "expense-g@example.com")

    response = await client.patch(f"/api/expenses/{entry_id}", json={"amount": "1"})
    assert response.status_code == 404
