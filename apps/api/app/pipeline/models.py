"""Shared data shapes passed between pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

Severity = Literal["info", "warning", "error"]


class RawCityRecord(BaseModel):
    """A single extracted, type-validated row. Field-level validation
    (types, required-ness) happens here; range/outlier checks happen
    separately in ``outliers.py`` so a merely unusual value is a warning,
    not something that fails parsing.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    city: str
    state: str
    population: int | None = None
    median_gross: Decimal
    sqm_cold: Decimal
    avg_apartment_size: Decimal
    groceries_month: Decimal
    transport_month: Decimal
    utilities_month: Decimal
    inflation_rate: Decimal
    year: int


class TransformedCityRecord(BaseModel):
    """A validated record plus values derived for the reference-household
    comparison, computed with the exact same formulas the personal
    dashboard uses (packages/analytics), not a separate calculation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    record: RawCityRecord
    estimated_monthly_rent: Decimal
    reference_net_income: Decimal
    reference_disposable_income: Decimal


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    rule_key: str
    message: str
    city: str | None = None
    field: str | None = None
    observed_value: str | None = None
    expected_range: str | None = None
