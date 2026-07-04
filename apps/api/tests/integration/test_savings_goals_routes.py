"""Savings goal CRUD and progress computation from contributions."""

from __future__ import annotations

from httpx import AsyncClient

from tests.helpers import register_and_login


async def test_create_goal_starts_at_zero_progress(client: AsyncClient) -> None:
    await register_and_login(client, "goal-a@example.com")
    create_response = await client.post(
        "/api/savings-goals",
        json={"name": "Urlaub", "target_amount": "2000.00", "target_date": "2026-12-01"},
    )
    assert create_response.status_code == 201, create_response.text

    list_response = await client.get("/api/savings-goals")
    progress = list_response.json()[0]
    assert progress["current_amount"] == "0.00"
    assert progress["progress_pct"] == "0.0"
    assert progress["projected_completion_date"] is None


async def test_contribution_increases_current_amount_and_progress(client: AsyncClient) -> None:
    await register_and_login(client, "goal-b@example.com")
    create_response = await client.post(
        "/api/savings-goals", json={"name": "Notgroschen", "target_amount": "1000.00"}
    )
    goal_id = create_response.json()["id"]

    contribution_response = await client.post(
        f"/api/savings-goals/{goal_id}/contributions",
        json={"amount": "250.00", "contributed_on": "2026-06-01"},
    )
    assert contribution_response.status_code == 201

    list_response = await client.get("/api/savings-goals")
    progress = list_response.json()[0]
    assert progress["current_amount"] == "250.00"
    assert progress["progress_pct"] == "25.0"


async def test_goal_marked_complete_when_target_reached(client: AsyncClient) -> None:
    await register_and_login(client, "goal-c@example.com")
    create_response = await client.post(
        "/api/savings-goals", json={"name": "Fahrrad", "target_amount": "500.00"}
    )
    goal_id = create_response.json()["id"]

    await client.post(
        f"/api/savings-goals/{goal_id}/contributions",
        json={"amount": "500.00", "contributed_on": "2026-06-01"},
    )

    list_response = await client.get("/api/savings-goals")
    progress = list_response.json()[0]
    assert progress["current_amount"] == "500.00"
    assert progress["projected_completion_date"] == "2026-06-01"


async def test_contribution_to_someone_elses_goal_returns_404(client: AsyncClient) -> None:
    await register_and_login(client, "goal-d@example.com")
    create_response = await client.post(
        "/api/savings-goals", json={"name": "Privat", "target_amount": "500.00"}
    )
    goal_id = create_response.json()["id"]

    await client.post("/api/auth/logout")
    await register_and_login(client, "goal-e@example.com")

    response = await client.post(
        f"/api/savings-goals/{goal_id}/contributions",
        json={"amount": "50.00", "contributed_on": "2026-06-01"},
    )
    assert response.status_code == 404


async def test_update_and_delete_goal(client: AsyncClient) -> None:
    await register_and_login(client, "goal-f@example.com")
    create_response = await client.post(
        "/api/savings-goals", json={"name": "Auto", "target_amount": "10000.00"}
    )
    goal_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/savings-goals/{goal_id}", json={"target_amount": "12000.00"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["target_amount"] == "12000.00"

    delete_response = await client.delete(f"/api/savings-goals/{goal_id}")
    assert delete_response.status_code == 204

    list_response = await client.get("/api/savings-goals")
    assert list_response.json() == []


async def test_delete_contribution(client: AsyncClient) -> None:
    await register_and_login(client, "goal-g@example.com")
    create_response = await client.post(
        "/api/savings-goals", json={"name": "Urlaub", "target_amount": "1000.00"}
    )
    goal_id = create_response.json()["id"]

    contribution_response = await client.post(
        f"/api/savings-goals/{goal_id}/contributions",
        json={"amount": "100.00", "contributed_on": "2026-06-01"},
    )
    contribution_id = contribution_response.json()["id"]

    delete_response = await client.delete(
        f"/api/savings-goals/{goal_id}/contributions/{contribution_id}"
    )
    assert delete_response.status_code == 204

    list_response = await client.get("/api/savings-goals")
    assert list_response.json()[0]["current_amount"] == "0.00"
