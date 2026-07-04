"""Disposable income: what is left after income minus expenses.

Used both by the personal dashboard (total income entries minus total expense
entries for a month) and by the data pipeline's reference-household
calculation (net income minus a fixed set of reference living costs), so both
paths share exactly one formula.
"""

from __future__ import annotations

from decimal import Decimal


def disposable_income(total_income: Decimal, total_expenses: Decimal) -> Decimal:
    """Income minus expenses. May be negative — a negative result is a valid,
    meaningful signal (feeds the ``negative_cash_flow`` insight rule), not an error.
    """
    return total_income - total_expenses


def reference_household_disposable_income(
    net_income: Decimal,
    rent: Decimal,
    utilities: Decimal,
    groceries: Decimal,
    transport: Decimal,
) -> Decimal:
    """Disposable income for a single-adult reference household used in city
    comparisons: net income minus the four core reference living-cost figures.
    """
    return disposable_income(net_income, rent + utilities + groceries + transport)
