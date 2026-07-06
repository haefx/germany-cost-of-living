"""Schema validation excludes malformed rows; outlier bounds only warn."""

from __future__ import annotations

from pathlib import Path

from app.pipeline.adapters.local_reference_csv import LocalReferenceCsvAdapter
from app.pipeline.stages import extract
from app.pipeline.stages import validate as validate_stage


def _validate_fixture(fixture_csv_path: Path):
    raw_rows = extract.run(LocalReferenceCsvAdapter(fixture_csv_path))
    return validate_stage.run(raw_rows)


def test_well_formed_row_passes_without_issues(fixture_csv_path: Path) -> None:
    records, issues = _validate_fixture(fixture_csv_path)
    testhausen = next(r for r in records if r.city == "Testhausen")
    assert testhausen is not None
    testhausen_issues = [i for i in issues if i.city == "Testhausen"]
    assert testhausen_issues == []


def test_out_of_range_value_is_a_warning_not_a_rejection(fixture_csv_path: Path) -> None:
    records, issues = _validate_fixture(fixture_csv_path)
    assert any(r.city == "Extremstadt" for r in records)  # still included

    warnings = [i for i in issues if i.city == "Extremstadt" and i.severity == "warning"]
    assert len(warnings) == 1
    assert warnings[0].rule_key == "median_gross_out_of_range"


def test_missing_required_field_is_an_error_and_excludes_the_row(
    fixture_csv_path: Path,
) -> None:
    records, issues = _validate_fixture(fixture_csv_path)
    assert all(r.city != "Fehlerdorf" for r in records)

    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 1
    assert errors[0].rule_key == "schema_validation_failed"


def test_three_rows_in_two_valid_records_out(fixture_csv_path: Path) -> None:
    records, _ = _validate_fixture(fixture_csv_path)
    assert len(records) == 2
