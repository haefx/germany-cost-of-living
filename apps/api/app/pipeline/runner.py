"""Orchestrates the full extract -> validate -> normalize -> transform ->
load -> publish run and records exactly one ``ImportRun`` plus zero or more
``ValidationResult`` rows for it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reference_data import ImportRun, ImportRunStatus, TriggeredBy, ValidationResult
from ..repositories.reference_data import create_import_run, get_or_create_data_source
from .adapters.local_reference_csv import LocalReferenceCsvAdapter
from .logging_setup import get_logger
from .models import ValidationIssue
from .stages import extract, load, normalize, publish, transform
from .stages import validate as validate_stage

logger = get_logger(__name__)

DATA_SOURCE_KEY = "local_reference_2023"
DATA_SOURCE_DISPLAY_NAME = "Reference city cost snapshot (2023)"
DATA_SOURCE_LICENSE_NOTE = (
    "Hand-compiled reference figures modeled on Destatis/Bundesagentur für "
    "Arbeit/BBSR Wohnatlas-style publications; not independently re-verified "
    "against a live licensed source this session. See DATA_LICENSES.md."
)
DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parents[4] / "data" / "reference" / "cities_reference_2023.csv"
)


@dataclass(frozen=True)
class PipelineResult:
    import_run: ImportRun
    issues: list[ValidationIssue]
    published: bool


async def _persist_issues(
    session: AsyncSession, import_run_id, issues: list[ValidationIssue]
) -> None:
    for issue in issues:
        session.add(
            ValidationResult(
                import_run_id=import_run_id,
                city_id=None,  # city rows may not exist yet at validation time
                severity=issue.severity,
                rule_key=issue.rule_key,
                message=issue.message,
                field=issue.field,
                observed_value=issue.observed_value,
                expected_range=issue.expected_range,
            )
        )
    await session.flush()


async def _ensure_data_source(session: AsyncSession):
    return await get_or_create_data_source(
        session,
        key=DATA_SOURCE_KEY,
        display_name=DATA_SOURCE_DISPLAY_NAME,
        url=None,
        description="Reference city cost-of-living snapshot bundled with the application.",
        license_note=DATA_SOURCE_LICENSE_NOTE,
        is_live_integration=False,
    )


async def run_pipeline(
    session: AsyncSession,
    *,
    csv_path: Path = DEFAULT_CSV_PATH,
    triggered_by: TriggeredBy = TriggeredBy.CLI,
    publish_on_success: bool = True,
) -> PipelineResult:
    """Runs extract through load (and publish, if requested and eligible).
    Always creates exactly one ``ImportRun``. Raises nothing on data
    problems — those become ``error``-severity ``ValidationResult`` rows and
    an unpublished (or ``failed``) run instead.
    """
    data_source = await _ensure_data_source(session)
    import_run = await create_import_run(session, data_source.id, triggered_by)

    try:
        raw_rows = extract.run(LocalReferenceCsvAdapter(csv_path))
        valid_records, issues = validate_stage.run(raw_rows)
        normalized = normalize.run(valid_records)
        transformed = transform.run(normalized)
        rows_loaded = await load.run(session, transformed, import_run.id)

        await _persist_issues(session, import_run.id, issues)

        has_errors = any(issue.severity == "error" for issue in issues)
        import_run.rows_extracted = len(raw_rows)
        import_run.rows_loaded = rows_loaded
        import_run.rows_rejected = len(raw_rows) - len(valid_records)
        import_run.status = ImportRunStatus.PARTIAL if has_errors else ImportRunStatus.SUCCESS
        import_run.finished_at = datetime.now(UTC)

        published = False
        if publish_on_success:
            published = await publish.run(session, import_run, has_errors)

        await session.flush()
        logger.info(
            "pipeline_run_complete",
            import_run_id=str(import_run.id),
            status=import_run.status,
            published=published,
        )
        return PipelineResult(import_run=import_run, issues=issues, published=published)

    except Exception as exc:
        import_run.status = ImportRunStatus.FAILED
        import_run.error_message = str(exc)
        import_run.finished_at = datetime.now(UTC)
        await session.flush()
        logger.exception("pipeline_run_failed", import_run_id=str(import_run.id))
        return PipelineResult(import_run=import_run, issues=[], published=False)


async def run_validate_only(
    session: AsyncSession, *, csv_path: Path = DEFAULT_CSV_PATH
) -> tuple[int, list[ValidationIssue]]:
    """Extract + validate only — never loads or publishes. Used to sanity
    check an updated reference file before committing it.
    """
    raw_rows = extract.run(LocalReferenceCsvAdapter(csv_path))
    valid_records, issues = validate_stage.run(raw_rows)
    return len(valid_records), issues
