"""Integration tests for the full pipeline run: loading, publishing, and the
no-partial-publication-after-failed-validation guarantee.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo import City
from app.models.reference_data import ImportRunStatus, SalarySnapshot
from app.pipeline.runner import DATA_SOURCE_KEY, DEFAULT_CSV_PATH, run_pipeline
from app.repositories.reference_data import get_latest_published_run


async def test_clean_source_publishes_successfully(db_session: AsyncSession) -> None:
    result = await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)

    assert result.import_run.status == ImportRunStatus.SUCCESS
    assert result.published is True
    assert result.import_run.rows_loaded == 10
    assert result.import_run.rows_rejected == 0


async def test_run_creates_cities_and_snapshots(db_session: AsyncSession) -> None:
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)

    cities = (await db_session.execute(select(City))).scalars().all()
    assert len(cities) == 10

    snapshots = (await db_session.execute(select(SalarySnapshot))).scalars().all()
    assert len(snapshots) == 10


async def test_running_twice_does_not_duplicate_cities_but_keeps_snapshot_history(
    db_session: AsyncSession,
) -> None:
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)
    await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)

    cities = (await db_session.execute(select(City))).scalars().all()
    assert len(cities) == 10  # get-or-create, not duplicated

    snapshots = (await db_session.execute(select(SalarySnapshot))).scalars().all()
    assert len(snapshots) == 20  # history preserved, not overwritten


async def test_source_with_errors_is_not_published(
    db_session: AsyncSession, fixture_csv_path: Path
) -> None:
    result = await run_pipeline(db_session, csv_path=fixture_csv_path)

    assert result.import_run.status == ImportRunStatus.PARTIAL
    assert result.published is False
    assert result.import_run.rows_loaded == 2
    assert result.import_run.rows_rejected == 1


async def test_a_failed_validation_does_not_overwrite_the_last_published_run(
    db_session: AsyncSession, fixture_csv_path: Path
) -> None:
    good_result = await run_pipeline(db_session, csv_path=DEFAULT_CSV_PATH)
    await run_pipeline(db_session, csv_path=fixture_csv_path)

    latest_published = await get_latest_published_run(db_session, DATA_SOURCE_KEY)
    assert latest_published is not None
    assert latest_published.id == good_result.import_run.id
