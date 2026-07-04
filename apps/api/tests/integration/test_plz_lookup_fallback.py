"""The postal-code lookup degrades gracefully when the upstream API is
unavailable — it never raises, and the endpoint returns a normal 200 with
found=False rather than an error.
"""

from __future__ import annotations

import httpx
import pytest
from httpx import AsyncClient

from app.integrations.plz_lookup import PlzLookupResult, resolve_postal_code
from tests.helpers import register_and_login


class _TimingOutAdapter:
    async def lookup(self, postal_code: str) -> PlzLookupResult:
        raise httpx.TimeoutException("simulated timeout")


class _WorkingAdapter:
    async def lookup(self, postal_code: str) -> PlzLookupResult:
        return PlzLookupResult(postal_code=postal_code, city="Berlin", state="Berlin")


async def test_resolve_postal_code_returns_none_on_timeout_without_raising() -> None:
    result = await resolve_postal_code(_TimingOutAdapter(), "10115")
    assert result is None


async def test_resolve_postal_code_returns_the_result_on_success() -> None:
    result = await resolve_postal_code(_WorkingAdapter(), "10115")
    assert result is not None
    assert result.city == "Berlin"


async def test_plz_endpoint_returns_200_with_found_false_when_lookup_fails(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.routers.cities as cities_router

    monkeypatch.setattr(cities_router, "_plz_adapter", _TimingOutAdapter())
    await register_and_login(client, "plz-a@example.com")

    response = await client.get("/api/plz/10115")
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False
    assert body["city"] is None


async def test_plz_endpoint_returns_city_when_lookup_succeeds(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.routers.cities as cities_router

    monkeypatch.setattr(cities_router, "_plz_adapter", _WorkingAdapter())
    await register_and_login(client, "plz-b@example.com")

    response = await client.get("/api/plz/10115")
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["city"] == "Berlin"
