"""Registration, login, password reset, and real session revocation on logout."""

from __future__ import annotations

from httpx import AsyncClient

from app.security import manager as manager_module


async def _register(
    client: AsyncClient, email: str, password: str = "correct-horse-battery"
) -> None:
    response = await client.post("/api/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201, response.text


async def test_register_creates_an_account(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "correct-horse-battery"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body
    assert body["is_demo"] is False


async def test_login_with_correct_password_succeeds(client: AsyncClient) -> None:
    await _register(client, "bob@example.com")
    response = await client.post(
        "/api/auth/login",
        data={"username": "bob@example.com", "password": "correct-horse-battery"},
    )
    assert response.status_code == 204
    assert "gcol_session_v2" in response.cookies


async def test_login_with_wrong_password_gives_generic_error(client: AsyncClient) -> None:
    await _register(client, "carol@example.com")
    response = await client.post(
        "/api/auth/login",
        data={"username": "carol@example.com", "password": "totally-wrong"},
    )
    assert response.status_code == 400
    # Generic error, not "wrong password" vs "no such user" — avoids account enumeration.
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


async def test_login_with_unknown_email_gives_the_same_generic_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        data={"username": "no-such-user@example.com", "password": "whatever"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


async def test_logout_revokes_the_session_immediately(client: AsyncClient) -> None:
    await _register(client, "dave@example.com")
    login_response = await client.post(
        "/api/auth/login",
        data={"username": "dave@example.com", "password": "correct-horse-battery"},
    )
    assert login_response.status_code == 204

    me_response = await client.get("/api/users/me")
    assert me_response.status_code == 200

    logout_response = await client.post("/api/auth/logout")
    assert logout_response.status_code == 204

    me_after_logout = await client.get("/api/users/me")
    assert me_after_logout.status_code == 401


async def test_password_reset_flow_changes_the_password(
    client: AsyncClient, monkeypatch: object
) -> None:
    captured_token: dict[str, str] = {}

    async def fake_on_after_forgot_password(self, user, token, request=None) -> None:
        captured_token["token"] = token

    monkeypatch.setattr(
        manager_module.UserManager, "on_after_forgot_password", fake_on_after_forgot_password
    )

    await _register(client, "erin@example.com")

    forgot_response = await client.post(
        "/api/auth/forgot-password", json={"email": "erin@example.com"}
    )
    assert forgot_response.status_code == 202
    assert "token" in captured_token

    reset_response = await client.post(
        "/api/auth/reset-password",
        json={"token": captured_token["token"], "password": "a-brand-new-password"},
    )
    assert reset_response.status_code == 200

    old_password_login = await client.post(
        "/api/auth/login",
        data={"username": "erin@example.com", "password": "correct-horse-battery"},
    )
    assert old_password_login.status_code == 400

    new_password_login = await client.post(
        "/api/auth/login",
        data={"username": "erin@example.com", "password": "a-brand-new-password"},
    )
    assert new_password_login.status_code == 204
