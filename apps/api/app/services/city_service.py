"""City comparison and data-source freshness, computed from the latest
*published* import run only — never a bare ``MAX(year)``, and never from
an unpublished or failed run.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from analytics.disposable_income import reference_household_disposable_income
from analytics.net_income import estimate_net_income
from analytics.rent_burden import rent_burden_pct
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import Base
from ..models.geo import City
from ..models.reference_data import (
    CostSnapshot,
    DataSource,
    ImportRun,
    InflationSnapshot,
    RentSnapshot,
    SalarySnapshot,
)
from ..pipeline.runner import DATA_SOURCE_KEY
from ..repositories.reference_data import get_latest_published_run
from ..schemas.city import CityComparisonRead, DataSourceStatusRead

# Matches the insights engine's own "outdated reference data" threshold
# (packages/analytics/analytics/insights/models.py) — kept as a separate
# constant here since the two live in different layers, not because the
# number should ever drift apart.
REFERENCE_DATA_MAX_AGE_DAYS = 548


async def get_city_comparisons(session: AsyncSession) -> list[CityComparisonRead]:
    latest_run = await get_latest_published_run(session, DATA_SOURCE_KEY)
    if latest_run is None:
        return []

    cities = (await session.execute(select(City))).scalars().all()
    results: list[CityComparisonRead] = []

    for city in cities:
        salary = await _snapshot_for(session, SalarySnapshot, city.id, latest_run.id)
        rent = await _snapshot_for(session, RentSnapshot, city.id, latest_run.id)
        cost = await _snapshot_for(session, CostSnapshot, city.id, latest_run.id)
        if salary is None or rent is None or cost is None:
            continue

        estimated_monthly_rent = (rent.sqm_cold * rent.avg_apartment_size).quantize(Decimal("0.01"))
        net_income = estimate_net_income(salary.median_gross).net_monthly
        disposable_income = reference_household_disposable_income(
            net_income=net_income,
            rent=estimated_monthly_rent,
            utilities=cost.utilities_month,
            groceries=cost.groceries_month,
            transport=cost.transport_month,
        )

        results.append(
            CityComparisonRead(
                city_id=city.id,
                name=city.name,
                state=city.state,
                population=city.population,
                year=salary.year,
                median_gross=salary.median_gross,
                estimated_monthly_rent=estimated_monthly_rent,
                sqm_cold=rent.sqm_cold,
                avg_apartment_size=rent.avg_apartment_size,
                groceries_month=cost.groceries_month,
                transport_month=cost.transport_month,
                utilities_month=cost.utilities_month,
                inflation_rate=await _inflation_rate_for(session, city.id, latest_run.id),
                reference_net_income=net_income,
                reference_disposable_income=disposable_income,
                rent_burden_pct=rent_burden_pct(estimated_monthly_rent, net_income),
            )
        )

    results.sort(key=lambda item: item.reference_disposable_income, reverse=True)
    return results


async def _snapshot_for[SnapshotModel: Base](
    session: AsyncSession,
    model: type[SnapshotModel],
    city_id: uuid.UUID,
    import_run_id: uuid.UUID,
) -> SnapshotModel | None:
    # SQLAlchemy's declarative attributes are InstrumentedAttribute
    # descriptors at the class level, not the Mapped[X] instance-level type,
    # so a Protocol expressing "has city_id and import_run_id" cannot
    # structurally match the four snapshot models without the dedicated
    # SQLAlchemy mypy plugin. Correctness here is enforced by the
    # pipeline/city-comparison integration tests instead.
    result = await session.execute(
        select(model).where(
            model.city_id == city_id,  # type: ignore[attr-defined]
            model.import_run_id == import_run_id,  # type: ignore[attr-defined]
        )
    )
    return result.scalar_one_or_none()


async def _inflation_rate_for(session: AsyncSession, city_id: uuid.UUID, import_run_id: uuid.UUID):
    snapshot = await _snapshot_for(session, InflationSnapshot, city_id, import_run_id)
    return snapshot.rate_pct if snapshot else None


async def get_data_source_statuses(session: AsyncSession) -> list[DataSourceStatusRead]:
    data_sources = (await session.execute(select(DataSource))).scalars().all()
    statuses = []
    for data_source in data_sources:
        latest_run = (
            await session.execute(
                select(ImportRun)
                .where(
                    ImportRun.data_source_id == data_source.id, ImportRun.published_at.is_not(None)
                )
                .order_by(ImportRun.published_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        age_days = None
        is_stale = False
        reference_year = None
        if latest_run is not None and latest_run.published_at is not None:
            age_days = (datetime.now(UTC) - latest_run.published_at).days
            is_stale = age_days > REFERENCE_DATA_MAX_AGE_DAYS
            any_salary_snapshot = (
                await session.execute(
                    select(SalarySnapshot.year)
                    .where(SalarySnapshot.import_run_id == latest_run.id)
                    .limit(1)
                )
            ).scalar_one_or_none()
            reference_year = any_salary_snapshot

        statuses.append(
            DataSourceStatusRead(
                key=data_source.key,
                display_name=data_source.display_name,
                url=data_source.url,
                license_note=data_source.license_note,
                is_live_integration=data_source.is_live_integration,
                last_published_at=latest_run.published_at if latest_run else None,
                reference_year=reference_year,
                age_days=age_days,
                is_stale=is_stale,
            )
        )
    return statuses
