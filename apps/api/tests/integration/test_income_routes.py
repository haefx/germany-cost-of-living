"""Income entry CRUD, validation, and recurrence handling."""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import category_id_by_name, register_and_login


async def test_create_and_list_income_entry(client: AsyncClient) -> None:
    await register_and_login(client, "income-a@example.com")
    category_id = await category_id_by_name(client, "Gehalt")

    create_response = await client.post(
        "/api/income",
        json={
            "label": "Juni-Gehalt",
            "amount": "3500.00",
            "entry_date": "2026-06-01",
            "category_id": category_id,
        },
    )
    assert create_response.status_code == 201, create_response.text
    body = create_response.json()
    assert body["amount"] == "3500.00"
    assert body["is_recurring"] is False

    list_response = await client.get("/api/income")
    assert any(entry["id"] == body["id"] for entry in list_response.json())


async def test_negative_amount_is_rejected(client: AsyncClient) -> None:
    await register_and_login(client, "income-b@example.com")
    response = await client.post(
        "/api/income",
        json={"label": "Invalid", "amount": "-100", "entry_date": "2026-06-01"},
    )
    assert response.status_code == 422


async def test_recurring_entry_requires_a_recurrence_rule(client: AsyncClient) -> None:
    await register_and_login(client, "income-c@example.com")
    response = await client.post(
        "/api/income",
        json={
            "label": "Gehalt",
            "amount": "3000",
            "entry_date": "2026-06-01",
            "is_recurring": True,
        },
    )
    assert response.status_code == 422


async def test_creating_a_recurring_entry_creates_its_rule(client: AsyncClient) -> None:
    await register_and_login(client, "income-d@example.com")
    response = await client.post(
        "/api/income",
        json={
            "label": "Gehalt",
            "amount": "3000",
            "entry_date": "2026-01-01",
            "is_recurring": True,
            "recurrence": {"frequency": "monthly", "interval_count": 1, "start_date": "2026-01-01"},
        },
    )
    assert response.status_code == 201
    assert response.json()["recurrence_rule_id"] is not None


async def test_recurring_entry_appears_in_a_later_months_listing(client: AsyncClient) -> None:
    await register_and_login(client, "income-e@example.com")
    create_response = await client.post(
        "/api/income",
        json={
            "label": "Gehalt",
            "amount": "3000",
            "entry_date": "2026-01-01",
            "is_recurring": True,
            "recurrence": {"frequency": "monthly", "interval_count": 1, "start_date": "2026-01-01"},
        },
    )
    entry_id = create_response.json()["id"]

    june_response = await client.get("/api/income", params={"month": "2026-06-15"})
    june_ids = [entry["id"] for entry in june_response.json()]
    assert entry_id in june_ids


async def test_weekly_recurring_entry_is_aggregated_by_occurrences(client: AsyncClient) -> None:
    await register_and_login(client, "income-weekly@example.com")
    await client.post(
        "/api/income",
        json={
            "label": "Wochenverdienst",
            "amount": "100.00",
            "entry_date": "2026-06-01",
            "is_recurring": True,
            "recurrence": {
                "frequency": "weekly",
                "interval_count": 1,
                "start_date": "2026-06-01",
            },
        },
    )

    response = await client.get("/api/income", params={"month": "2026-06-01"})
    assert response.status_code == 200
    assert response.json()[0]["amount"] == "500.00"


async def test_update_income_entry(client: AsyncClient) -> None:
    await register_and_login(client, "income-f@example.com")
    create_response = await client.post(
        "/api/income", json={"label": "Bonus", "amount": "500", "entry_date": "2026-06-01"}
    )
    entry_id = create_response.json()["id"]

    update_response = await client.patch(f"/api/income/{entry_id}", json={"amount": "600.00"})
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == "600.00"


async def test_delete_income_entry(client: AsyncClient) -> None:
    await register_and_login(client, "income-g@example.com")
    create_response = await client.post(
        "/api/income", json={"label": "Bonus", "amount": "500", "entry_date": "2026-06-01"}
    )
    entry_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/income/{entry_id}")
    assert delete_response.status_code == 204

    list_response = await client.get("/api/income")
    assert all(entry["id"] != entry_id for entry in list_response.json())


async def test_unauthenticated_requests_are_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/income")
    assert response.status_code == 401
