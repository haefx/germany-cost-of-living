"""Publishes an import run only if loading succeeded and no error-severity
validation issue exists for it — no partial publication after a failed
validation, and the app only ever reads published runs.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ...models.reference_data import ImportRun
from ..logging_setup import get_logger

logger = get_logger(__name__)


async def run(session: AsyncSession, import_run: ImportRun, has_errors: bool) -> bool:
    if has_errors:
        logger.warning("publish_skipped_due_to_errors", import_run_id=str(import_run.id))
        return False

    import_run.published_at = datetime.now(UTC)
    await session.flush()
    logger.info("publish_complete", import_run_id=str(import_run.id))
    return True
