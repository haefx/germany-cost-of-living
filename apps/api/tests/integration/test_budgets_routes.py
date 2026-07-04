"""Budget CRUD and the computed planned-vs-actual status."""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import category_id_by_name, register_and_login


async def test_create_budget_and_see_it_in_status_list(client: AsyncClient) -> None:
    await register_and_login(client, "budget-a@example.com")
    category_id = await category_id_by_name(client, "Lebensmittel")

    create_response = await client.post(
        "/api/budgets",
        json={
            "category_id": category_id,
            "monthly_limit": "300.00",
            "effective_from": "2026-06-01",
        },
    )
    assert create_response.status_code == 201, create_response.text

    status_response = await client.get("/api/budgets", params={"month": "2026-06-15"})
    statuses = status_response.json()
    assert len(statuses) == 1
    assert statuses[0]["actual_spent"] == "0.00"
    assert statuses[0]["remaining"] == "300.00"
    assert statuses[0]["is_over_budget"] is False


async def test_budget_status_reflects_actual_spending(client: AsyncClient) -> None:
    await register_and_login(client, "budget-b@example.com")
    category_id = await category_id_by_name(client, "Lebensmittel")

    await client.post(
        "/api/budgets",
        json={
            "category_id": category_id,
            "monthly_limit": "300.00",
            "effective_from": "2026-06-01",
        },
    )
    await client.post(
        "/api/expenses",
        json={
            "label": "Einkauf",
            "amount": "120.00",
            "entry_date": "2026-06-10",
            "category_id": category_id,
        },
    )

    status_response = await client.get("/api/budgets", params={"month": "2026-06-15"})
    status = status_response.json()[0]
    assert status["actual_spent"] == "120.00"
    assert status["remaining"] == "180.00"
    assert status["is_over_budget"] is False


async def test_budget_flags_over_budget_when_spending_exceeds_limit(client: AsyncClient) -> None:
    await register_and_login(client, "budget-c@example.com")
    category_id = await category_id_by_name(client, "Lebensmittel")

    await client.post(
        "/api/budgets",
        json={
            "category_id": category_id,
            "monthly_limit": "100.00",
            "effective_from": "2026-06-01",
        },
    )
    await client.post(
        "/api/expenses",
        json={
            "label": "Großeinkauf",
            "amount": "150.00",
            "entry_date": "2026-06-10",
            "category_id": category_id,
        },
    )

    status_response = await client.get("/api/budgets", params={"month": "2026-06-15"})
    status = status_response.json()[0]
    assert status["is_over_budget"] is True
    assert status["remaining"] == "-50.00"


async def test_update_and_delete_budget(client: AsyncClient) -> None:
    await register_and_login(client, "budget-d@example.com")
    category_id = await category_id_by_name(client, "Freizeit")

    create_response = await client.post(
        "/api/budgets",
        json={"category_id": category_id, "monthly_limit": "50.00", "effective_from": "2026-06-01"},
    )
    budget_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/budgets/{budget_id}", json={"monthly_limit": "75.00"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["monthly_limit"] == "75.00"

    delete_response = await client.delete(f"/api/budgets/{budget_id}")
    assert delete_response.status_code == 204

    status_response = await client.get("/api/budgets", params={"month": "2026-06-15"})
    assert status_response.json() == []
