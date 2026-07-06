"""Data pipeline commands: ``python -m app.pipeline.cli refresh|validate|status``
(wired as ``make data-refresh`` / ``make data-validate`` / ``make data-status``).
"""

from __future__ import annotations

import asyncio

import typer

from ..db import async_session_factory
from ..repositories.reference_data import get_latest_run
from .runner import DATA_SOURCE_KEY, TriggeredBy, run_pipeline, run_validate_only

app = typer.Typer(help="Data pipeline commands for the public reference dataset.")


@app.command()
def refresh() -> None:
    """Run the full extract-to-publish pipeline and record a new import run."""
    asyncio.run(_refresh())


async def _refresh() -> None:
    async with async_session_factory() as session:
        result = await run_pipeline(session, triggered_by=TriggeredBy.CLI)
        await session.commit()
        error_count = sum(1 for issue in result.issues if issue.severity == "error")
        warning_count = sum(1 for issue in result.issues if issue.severity == "warning")
        typer.echo(f"Status: {result.import_run.status}")
        typer.echo(f"Rows loaded: {result.import_run.rows_loaded}")
        typer.echo(f"Published: {result.published}")
        typer.echo(f"Validation: {error_count} error(s), {warning_count} warning(s)")


@app.command()
def validate() -> None:
    """Extract and validate the reference file only — nothing is loaded or published."""
    asyncio.run(_validate())


async def _validate() -> None:
    async with async_session_factory() as session:
        valid_count, issues = await run_validate_only(session)
        typer.echo(f"Valid rows: {valid_count}")
        for issue in issues:
            typer.echo(f"  [{issue.severity}] {issue.rule_key}: {issue.message}")


@app.command()
def status() -> None:
    """Show the most recent import run for the reference data source."""
    asyncio.run(_status())


async def _status() -> None:
    async with async_session_factory() as session:
        latest = await get_latest_run(session, DATA_SOURCE_KEY)
        if latest is None:
            typer.echo("No import runs yet. Run `make data-refresh` first.")
            return
        typer.echo(f"Status: {latest.status}")
        typer.echo(f"Started: {latest.started_at}")
        typer.echo(f"Finished: {latest.finished_at}")
        typer.echo(f"Published: {latest.published_at}")
        typer.echo(
            "Rows extracted/loaded/rejected: "
            f"{latest.rows_extracted}/{latest.rows_loaded}/{latest.rows_rejected}"
        )


if __name__ == "__main__":
    app()
