"""Derives the figures shown in the city comparison, using the exact same
formulas the personal dashboard uses — this is the one place the pipeline
imports packages/analytics, so there is a single source of truth for
"disposable income", not a second implementation living in the pipeline.
"""

from __future__ import annotations

from analytics.disposable_income import reference_household_disposable_income
from analytics.net_income import estimate_net_income

from ..models import RawCityRecord, TransformedCityRecord


def run(records: list[RawCityRecord]) -> list[TransformedCityRecord]:
    transformed = []
    for record in records:
        estimated_monthly_rent = record.sqm_cold * record.avg_apartment_size
        net_income = estimate_net_income(record.median_gross).net_monthly
        disposable_income = reference_household_disposable_income(
            net_income=net_income,
            rent=estimated_monthly_rent,
            utilities=record.utilities_month,
            groceries=record.groceries_month,
            transport=record.transport_month,
        )
        transformed.append(
            TransformedCityRecord(
                record=record,
                estimated_monthly_rent=estimated_monthly_rent,
                reference_net_income=net_income,
                reference_disposable_income=disposable_income,
            )
        )
    return transformed
