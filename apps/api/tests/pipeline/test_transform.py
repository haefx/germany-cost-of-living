"""Transform derives figures using packages/analytics — the same formulas
the personal dashboard uses, not a second implementation.
"""

from __future__ import annotations

from decimal import Decimal

from analytics.disposable_income import reference_household_disposable_income
from analytics.net_income import estimate_net_income

from app.pipeline.models import RawCityRecord
from app.pipeline.stages import transform


def _record(**overrides: object) -> RawCityRecord:
    defaults = dict(
        city="Testhausen",
        state="Testland",
        population=100000,
        median_gross=Decimal("3500"),
        sqm_cold=Decimal("15.0"),
        avg_apartment_size=Decimal("70"),
        groceries_month=Decimal("350"),
        transport_month=Decimal("90"),
        utilities_month=Decimal("220"),
        inflation_rate=Decimal("4.5"),
        year=2023,
    )
    defaults.update(overrides)
    return RawCityRecord(**defaults)


def test_estimated_rent_is_sqm_times_apartment_size() -> None:
    [result] = transform.run([_record()])
    assert result.estimated_monthly_rent == Decimal("15.0") * Decimal("70")


def test_disposable_income_matches_the_shared_analytics_formula() -> None:
    record = _record()
    [result] = transform.run([record])

    expected_net_income = estimate_net_income(record.median_gross).net_monthly
    expected_disposable = reference_household_disposable_income(
        net_income=expected_net_income,
        rent=record.sqm_cold * record.avg_apartment_size,
        utilities=record.utilities_month,
        groceries=record.groceries_month,
        transport=record.transport_month,
    )

    assert result.reference_net_income == expected_net_income
    assert result.reference_disposable_income == expected_disposable


def test_transform_preserves_the_original_record() -> None:
    record = _record(city="Anderestadt")
    [result] = transform.run([record])
    assert result.record.city == "Anderestadt"
