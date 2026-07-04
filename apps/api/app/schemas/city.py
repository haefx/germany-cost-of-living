"""Response schemas for city comparison, data-source freshness, and PLZ lookup."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CityComparisonRead(BaseModel):
    city_id: uuid.UUID
    name: str
    state: str
    population: int | None
    year: int
    median_gross: Decimal
    estimated_monthly_rent: Decimal
    sqm_cold: Decimal
    avg_apartment_size: Decimal
    groceries_month: Decimal
    transport_month: Decimal
    utilities_month: Decimal
    inflation_rate: Decimal
    reference_net_income: Decimal
    reference_disposable_income: Decimal
    rent_burden_pct: Decimal


class DataSourceStatusRead(BaseModel):
    key: str
    display_name: str
    url: str | None
    license_note: str | None
    is_live_integration: bool
    last_published_at: datetime | None
    reference_year: int | None
    age_days: int | None
    is_stale: bool


class PlzLookupResponse(BaseModel):
    found: bool
    postal_code: str
    city: str | None = None
    state: str | None = None
