"""Proves the router correctly assembles an InsightContext from real rows
and calls the shared engine — rule logic itself is tested in
packages/analytics/tests/insights/.
"""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import category_id_by_name, register_and_login


async def test_insights_endpoint_runs_without_any_data(client: AsyncClient) -> None:
    await register_and_login(client, "insights-a@example.com")
    response = await client.get("/api/insights", params={"month": "2026-06-15"})
    assert response.status_code == 200
    body = response.json()
    assert body["failed_rules"] == []
    # No income entered yet -> the onboarding nudge should fire.
    assert any(i["rule_key"] == "missing_inputs" for i in body["insights"])


async def test_insights_flags_negative_cash_flow(client: AsyncClient) -> None:
    await register_and_login(client, "insights-b@example.com")
    await client.post(
        "/api/income", json={"label": "Gehalt", "amount": "1000", "entry_date": "2026-06-01"}
    )
    await client.post(
        "/api/expenses", json={"label": "Miete", "amount": "1500", "entry_date": "2026-06-05"}
    )

    response = await client.get("/api/insights", params={"month": "2026-06-15"})
    insights = response.json()["insights"]
    assert any(i["rule_key"] == "negative_cash_flow" for i in insights)


async def test_insights_flags_budget_overrun(client: AsyncClient) -> None:
    await register_and_login(client, "insights-c@example.com")
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

    response = await client.get("/api/insights", params={"month": "2026-06-15"})
    insights = response.json()["insights"]
    overrun = next(i for i in insights if i["rule_key"] == "budget_overrun")
    assert overrun["estimated_savings_max"] == "50.00"


async def test_insights_flags_high_rent_burden(client: AsyncClient) -> None:
    await register_and_login(client, "insights-d@example.com")
    housing_category_id = await category_id_by_name(client, "Miete & Wohnen")

    await client.post(
        "/api/income", json={"label": "Gehalt", "amount": "2000", "entry_date": "2026-06-01"}
    )
    await client.post(
        "/api/expenses",
        json={
            "label": "Miete",
            "amount": "1200",
            "entry_date": "2026-06-01",
            "category_id": housing_category_id,
        },
    )

    response = await client.get("/api/insights", params={"month": "2026-06-15"})
    insights = response.json()["insights"]
    assert any(i["rule_key"] == "high_rent_burden" for i in insights)


async def test_insights_reflect_only_the_current_users_data(client: AsyncClient) -> None:
    await register_and_login(client, "insights-e@example.com")
    await client.post(
        "/api/income", json={"label": "Gehalt", "amount": "500", "entry_date": "2026-06-01"}
    )
    await client.post(
        "/api/expenses", json={"label": "Miete", "amount": "2000", "entry_date": "2026-06-01"}
    )

    await client.post("/api/auth/logout")
    await register_and_login(client, "insights-f@example.com")

    response = await client.get("/api/insights", params={"month": "2026-06-15"})
    insights = response.json()["insights"]
    assert not any(i["rule_key"] == "negative_cash_flow" for i in insights)


async def test_unauthenticated_requests_are_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/insights")
    assert response.status_code == 401
