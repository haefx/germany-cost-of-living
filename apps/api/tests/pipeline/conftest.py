from pathlib import Path

import pytest

FIXTURE_CSV = Path(__file__).resolve().parents[1] / "fixtures" / "reference_data_sample.csv"


@pytest.fixture
def fixture_csv_path() -> Path:
    return FIXTURE_CSV
