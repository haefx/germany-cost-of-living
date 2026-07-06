"""Range checks for the reference dataset.

A value outside its expected range is recorded as a *warning*, not
discarded — the old prototype's pipeline silently clamped values with
``.clip()``, hiding exactly the kind of bad-source-data problem this is
meant to surface.
"""

from __future__ import annotations

from decimal import Decimal

from .models import RawCityRecord, ValidationIssue

FIELD_BOUNDS: dict[str, tuple[Decimal, Decimal]] = {
    "median_gross": (Decimal("1500"), Decimal("10000")),
    "sqm_cold": (Decimal("5"), Decimal("50")),
    "avg_apartment_size": (Decimal("25"), Decimal("150")),
    "groceries_month": (Decimal("100"), Decimal("1000")),
    "transport_month": (Decimal("30"), Decimal("250")),
    "utilities_month": (Decimal("100"), Decimal("500")),
    "inflation_rate": (Decimal("0"), Decimal("20")),
}


def check_bounds(record: RawCityRecord) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field, (lower, upper) in FIELD_BOUNDS.items():
        value: Decimal = getattr(record, field)
        if value < lower or value > upper:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    rule_key=f"{field}_out_of_range",
                    message=(
                        f"{record.city}: {field}={value} is outside the expected "
                        f"range [{lower}, {upper}]"
                    ),
                    city=record.city,
                    field=field,
                    observed_value=str(value),
                    expected_range=f"[{lower}, {upper}]",
                )
            )
    return issues
