"""Affordability banding: how much of net income remains available.

A simple, transparent bucketing used for a single "how are things looking"
indicator on the dashboard. The thresholds are a product judgment call, not a
regulatory definition.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

AffordabilityLevel = Literal["critical", "tight", "moderate", "comfortable"]


def affordability_level(disposable: Decimal, net_income: Decimal) -> AffordabilityLevel:
    ratio = disposable / net_income if net_income > 0 else Decimal("0")
    if ratio < Decimal("0.10"):
        return "critical"
    if ratio < Decimal("0.25"):
        return "tight"
    if ratio < Decimal("0.45"):
        return "moderate"
    return "comfortable"
