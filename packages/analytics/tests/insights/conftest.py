from datetime import date
from decimal import Decimal

import pytest

from analytics.insights.models import InsightContext


@pytest.fixture
def base_context() -> InsightContext:
    return InsightContext(
        month=date(2026, 6, 1),
        total_income=Decimal("3000"),
        total_expenses=Decimal("2000"),
    )
