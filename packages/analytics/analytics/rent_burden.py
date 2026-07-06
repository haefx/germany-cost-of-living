"""Rent burden: the share of net income spent on rent."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

WARNING_THRESHOLD_PCT = Decimal("30")
CRITICAL_THRESHOLD_PCT = Decimal("40")


def rent_burden_pct(rent: Decimal, net_income: Decimal) -> Decimal:
    """Rent as a percentage of net income, rounded to one decimal place.

    Returns 0 when net income is zero or negative rather than raising, since
    this is a display value, not a validated financial guarantee.
    """
    if net_income <= 0:
        return Decimal("0.0")
    return (rent / net_income * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def rent_burden_level(pct: Decimal) -> str:
    """Returns "ok" | "warning" | "critical" based on the standard 30%/40% bands
    commonly used as a rule-of-thumb rent-burden reference in German housing
    policy discussion. Not a formal legal threshold.
    """
    if pct >= CRITICAL_THRESHOLD_PCT:
        return "critical"
    if pct >= WARNING_THRESHOLD_PCT:
        return "warning"
    return "ok"
