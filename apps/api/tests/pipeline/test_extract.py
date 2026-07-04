"""Extraction reads the local reference file only — no real HTTP calls
anywhere in the pipeline test suite.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.pipeline.adapters.local_reference_csv import LocalReferenceCsvAdapter, SourceReadError
from app.pipeline.stages import extract


def test_extract_reads_all_rows_from_the_fixture(fixture_csv_path: Path) -> None:
    rows = extract.run(LocalReferenceCsvAdapter(fixture_csv_path))
    assert len(rows) == 3
    assert rows[0]["city"] == "Testhausen"


def test_extract_raises_after_retries_on_a_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "does-not-exist.csv"
    with pytest.raises(SourceReadError):
        LocalReferenceCsvAdapter(missing_path).extract()
