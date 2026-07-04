"""Data access for the public reference-data domain: sources, import runs,
and the latest-published-snapshot lookup every read path uses.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reference_data import DataSource, ImportRun, ImportRunStatus, TriggeredBy


async def get_or_create_data_source(
    session: AsyncSession,
    key: str,
    display_name: str,
    *,
    url: str | None = None,
    description: str | None = None,
    license_note: str | None = None,
    is_live_integration: bool = False,
) -> DataSource:
    result = await session.execute(select(DataSource).where(DataSource.key == key))
    data_source = result.scalar_one_or_none()
    if data_source is not None:
        return data_source

    data_source = DataSource(
        key=key,
        display_name=display_name,
        url=url,
        description=description,
        license_note=license_note,
        is_live_integration=is_live_integration,
    )
    session.add(data_source)
    await session.flush()
    return data_source


async def create_import_run(
    session: AsyncSession, data_source_id: uuid.UUID, triggered_by: TriggeredBy
) -> ImportRun:
    import_run = ImportRun(
        data_source_id=data_source_id,
        status=ImportRunStatus.RUNNING,
        started_at=datetime.now(UTC),
        triggered_by=triggered_by,
    )
    session.add(import_run)
    await session.flush()
    return import_run


async def get_latest_published_run(session: AsyncSession, data_source_key: str) -> ImportRun | None:
    result = await session.execute(
        select(ImportRun)
        .join(DataSource, ImportRun.data_source_id == DataSource.id)
        .where(DataSource.key == data_source_key, ImportRun.published_at.is_not(None))
        .order_by(ImportRun.published_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_run(session: AsyncSession, data_source_key: str) -> ImportRun | None:
    result = await session.execute(
        select(ImportRun)
        .join(DataSource, ImportRun.data_source_id == DataSource.id)
        .where(DataSource.key == data_source_key)
        .order_by(ImportRun.started_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
