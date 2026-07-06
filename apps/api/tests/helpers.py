"""Small shared helpers for integration tests."""

from __future__ import annotations

from httpx import AsyncClient

PASSWORD = "correct-horse-battery"


async def register_and_login(client: AsyncClient, email: str) -> None:
    register_response = await client.post(
        "/api/auth/register", json={"email": email, "password": PASSWORD}
    )
    assert register_response.status_code == 201, register_response.text
    login_response = await client.post(
        "/api/auth/login", data={"username": email, "password": PASSWORD}
    )
    assert login_response.status_code == 204, login_response.text


async def category_id_by_name(client: AsyncClient, name: str) -> str:
    response = await client.get("/api/categories")
    for category in response.json():
        if category["name"] == name:
            return category["id"]
    raise AssertionError(f"Category {name!r} not found in /api/categories response")
