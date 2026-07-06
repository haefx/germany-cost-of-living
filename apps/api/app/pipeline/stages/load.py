"""Upserts cities and inserts new snapshot rows tied to the current import
run. Never deletes prior snapshots — history is preserved, unlike the
original prototype's pipeline, which wiped and re-inserted every run.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.geo import City
from ...models.reference_data import CostSnapshot, InflationSnapshot, RentSnapshot, SalarySnapshot
from ..logging_setup import get_logger
from ..models import TransformedCityRecord

logger = get_logger(__name__)


async def _get_or_create_city(
    session: AsyncSession, name: str, state: str, population: int | None
) -> City:
    result = await session.execute(select(City).where(City.name == name))
    city = result.scalar_one_or_none()
    if city is None:
        city = City(name=name, state=state, population=population)
        session.add(city)
        await session.flush()
    return city


async def run(
    session: AsyncSession, records: list[TransformedCityRecord], import_run_id: uuid.UUID
) -> int:
    rows_loaded = 0
    for item in records:
        record = item.record
        city = await _get_or_create_city(session, record.city, record.state, record.population)

        session.add(
            SalarySnapshot(
                city_id=city.id,
                import_run_id=import_run_id,
                median_gross=record.median_gross,
                year=record.year,
            )
        )
        session.add(
            RentSnapshot(
                city_id=city.id,
                import_run_id=import_run_id,
                sqm_cold=record.sqm_cold,
                avg_apartment_size=record.avg_apartment_size,
                year=record.year,
            )
        )
        session.add(
            CostSnapshot(
                city_id=city.id,
                import_run_id=import_run_id,
                groceries_month=record.groceries_month,
                transport_month=record.transport_month,
                utilities_month=record.utilities_month,
                year=record.year,
            )
        )
        session.add(
            InflationSnapshot(
                city_id=city.id,
                import_run_id=import_run_id,
                rate_pct=record.inflation_rate,
                year=record.year,
            )
        )
        rows_loaded += 1

    await session.flush()
    logger.info("load_complete", rows_loaded=rows_loaded)
    return rows_loaded
