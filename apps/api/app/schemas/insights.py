"""Response schema for the deterministic insights endpoint."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class InsightRead(BaseModel):
    rule_key: str
    severity: str
    title: str
    explanation: str
    evidence: dict[str, Any]
    confidence: str
    suggested_action: str
    assumptions: list[str]
    estimated_savings_min: Decimal | None
    estimated_savings_max: Decimal | None
    disclaimer: str


class InsightsResponse(BaseModel):
    month: str
    insights: list[InsightRead]
    failed_rules: list[str]
