"""Savings projection: deposits over time, with clearly separated hypothetical growth.

Per the product's financial-scenario rules, this must never be presented as a
guaranteed outcome. The default annual growth rate is 0% (pure deposits); any
non-zero rate is an explicit, user-chosen illustrative assumption, and the
output always separates ``deposited`` (fact) from ``growth`` (hypothetical)
so the UI can label them differently.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")


def _round_currency(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class SavingsProjectionYear:
    year: int
    deposited: Decimal
    growth: Decimal
    total: Decimal
    total_inflation_adjusted: Decimal | None = None


def project_savings(
    monthly_contribution: Decimal,
    years: int,
    annual_growth_rate: Decimal = Decimal("0"),
    annual_inflation_rate: Decimal | None = None,
) -> list[SavingsProjectionYear]:
    """Project a monthly contribution forward, compounding ``annual_growth_rate``
    monthly. With the default 0% rate, ``growth`` is always 0 and ``total``
    exactly equals cumulative deposits.

    Raises ``ValueError`` for negative contributions, years, or rates, since
    those inputs are meaningless for this projection rather than a valid edge case.
    """
    if monthly_contribution < 0:
        raise ValueError("monthly_contribution must not be negative")
    if years < 0:
        raise ValueError("years must not be negative")
    if annual_growth_rate < 0:
        raise ValueError("annual_growth_rate must not be negative")

    monthly_rate = annual_growth_rate / 12
    total = Decimal("0")
    deposited = Decimal("0")
    results: list[SavingsProjectionYear] = []

    for month in range(1, years * 12 + 1):
        total = total * (1 + monthly_rate) + monthly_contribution
        deposited += monthly_contribution
        if month % 12 == 0:
            year = month // 12
            growth = total - deposited
            inflation_adjusted = None
            if annual_inflation_rate is not None:
                deflator = (1 + annual_inflation_rate) ** year
                inflation_adjusted = _round_currency(total / deflator)
            results.append(
                SavingsProjectionYear(
                    year=year,
                    deposited=_round_currency(deposited),
                    growth=_round_currency(growth),
                    total=_round_currency(total),
                    total_inflation_adjusted=inflation_adjusted,
                )
            )
    return results
