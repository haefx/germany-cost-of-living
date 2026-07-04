"""City comparison and data-source endpoints reflect only published runs."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.pipeline.runner import DEFAULT_CSV_PATH, run_pipeline
from tests.helpers import register_and_login


async def test_cities_empty_before_any_pipeline_run(client: AsyncClient) -> None:
    await register_and_login(client, "cities-a@example.com")
    response = await client.get("/api/cities")
    assert response.status_code == 200
    assert response.json() == []


async def test_cities_list_reflects_the_published_run(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)
    await register_and_login(client, "cities-b@example.com")

    response = await client.get("/api/cities")
    assert response.status_code == 200
    cities = response.json()
    assert len(cities) == 10

    berlin = next(c for c in cities if c["name"] == "Berlin")
    assert berlin["median_gross"] == "3850.00"
    assert berlin["estimated_monthly_rent"] == "1188.00"  # 16.5 * 72
    assert berlin["reference_disposable_income"] is not None
    assert berlin["rent_burden_pct"] is not None


async def test_cities_are_sorted_by_disposable_income_descending(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)
    await register_and_login(client, "cities-c@example.com")

    response = await client.get("/api/cities")
    cities = response.json()
    incomes = [float(c["reference_disposable_income"]) for c in cities]
    assert incomes == sorted(incomes, reverse=True)


async def test_data_sources_reflects_the_published_run(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)
    await register_and_login(client, "cities-d@example.com")

    response = await client.get("/api/data-sources")
    assert response.status_code == 200
    sources = response.json()
    reference_source = next(s for s in sources if s["key"] == "local_reference_2023")
    assert reference_source["last_published_at"] is not None
    assert reference_source["is_stale"] is False
    assert reference_source["is_live_integration"] is False


async def test_unauthenticated_requests_are_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/cities")
    assert response.status_code == 401
