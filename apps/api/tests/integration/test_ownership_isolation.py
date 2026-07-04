"""Proves that one user cannot read, modify, or delete another user's data.

Categories are used as the concrete entity here because they already exist
end-to-end (repository, service, router); the same ``UserOwnedRepository``
base class backs every other personal-finance entity added later, so this
test exercises the shared mechanism, not category-specific logic.
"""

from __future__ import annotations

from httpx import AsyncClient

PASSWORD = "correct-horse-battery"


async def _register_and_login(client: AsyncClient, email: str) -> None:
    register_response = await client.post(
        "/api/auth/register", json={"email": email, "password": PASSWORD}
    )
    assert register_response.status_code == 201, register_response.text
    login_response = await client.post(
        "/api/auth/login", data={"username": email, "password": PASSWORD}
    )
    assert login_response.status_code == 204, login_response.text


async def test_owner_can_update_their_own_category(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")
    create_response = await client.post(
        "/api/categories", json={"name": "Haustier", "kind": "expense"}
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/categories/{category_id}", json={"name": "Haustierbedarf"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Haustierbedarf"


async def test_other_user_cannot_see_a_private_category_in_their_list(
    client: AsyncClient,
) -> None:
    await _register_and_login(client, "user-a@example.com")
    create_response = await client.post(
        "/api/categories", json={"name": "A-only Category", "kind": "expense"}
    )
    category_id = create_response.json()["id"]

    await client.post("/api/auth/logout")
    await _register_and_login(client, "user-b@example.com")

    list_response = await client.get("/api/categories")
    visible_ids = [category["id"] for category in list_response.json()]
    assert category_id not in visible_ids


async def test_other_user_cannot_update_a_private_category(client: AsyncClient) -> None:
    await _register_and_login(client, "user-c@example.com")
    create_response = await client.post(
        "/api/categories", json={"name": "C-only Category", "kind": "expense"}
    )
    category_id = create_response.json()["id"]

    await client.post("/api/auth/logout")
    await _register_and_login(client, "user-d@example.com")

    update_response = await client.patch(
        f"/api/categories/{category_id}", json={"name": "Hijacked"}
    )
    assert update_response.status_code == 404


async def test_other_user_cannot_delete_a_private_category(client: AsyncClient) -> None:
    await _register_and_login(client, "user-e@example.com")
    create_response = await client.post(
        "/api/categories", json={"name": "E-only Category", "kind": "expense"}
    )
    category_id = create_response.json()["id"]

    await client.post("/api/auth/logout")
    await _register_and_login(client, "user-f@example.com")

    delete_response = await client.delete(f"/api/categories/{category_id}")
    assert delete_response.status_code == 404


async def test_unauthenticated_request_is_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/categories")
    assert response.status_code == 401


async def test_global_default_categories_are_visible_to_every_user(
    client: AsyncClient,
) -> None:
    await _register_and_login(client, "user-g@example.com")
    response = await client.get("/api/categories")
    names = [category["name"] for category in response.json()]
    assert "Miete & Wohnen" in names
    assert "Gehalt" in names
