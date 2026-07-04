"""Shared data shapes for the deterministic insights engine.

``InsightContext`` is assembled by the API's service layer from real
database rows and passed into ``engine.run_all``. Every rule receives the
same context and returns zero or more ``Insight`` objects — rules never
query a database themselves, which is what keeps them unit-testable with
plain fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

Severity = Literal["info", "warning", "critical"]
Confidence = Literal["low", "medium", "high"]

STANDARD_DISCLAIMER = (
    "Automatisierte, regelbasierte Einschätzung auf Basis deiner eigenen Daten. "
    "Keine Finanz-, Steuer- oder Rechtsberatung."
)


@dataclass(frozen=True)
class Insight:
    rule_key: str
    severity: Severity
    title: str
    explanation: str
    evidence: dict[str, object]
    confidence: Confidence
    suggested_action: str
    assumptions: tuple[str, ...]
    estimated_savings_min: Decimal | None = None
    estimated_savings_max: Decimal | None = None
    disclaimer: str = STANDARD_DISCLAIMER


@dataclass(frozen=True)
class CategorySpending:
    category_id: str
    category_name: str
    current_amount: Decimal
    trailing_average: Decimal
    trailing_history: tuple[Decimal, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BudgetStatus:
    category_id: str
    category_name: str
    monthly_limit: Decimal
    actual_spent: Decimal


@dataclass(frozen=True)
class RecurringExpenseEntry:
    id: str
    category_id: str | None
    label: str
    amount: Decimal
    entry_date: date
    recurrence_rule_id: str


@dataclass(frozen=True)
class SavingsGoalStatus:
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None
    trailing_monthly_contribution_avg: Decimal


@dataclass(frozen=True)
class InsightContext:
    month: date
    total_income: Decimal
    total_expenses: Decimal
    net_income: Decimal | None = None
    previous_month_total_income: Decimal | None = None
    rent_amount: Decimal | None = None
    category_spending: tuple[CategorySpending, ...] = field(default_factory=tuple)
    trailing_total_expenses: tuple[Decimal, ...] = field(default_factory=tuple)
    budgets: tuple[BudgetStatus, ...] = field(default_factory=tuple)
    recurring_expenses: tuple[RecurringExpenseEntry, ...] = field(default_factory=tuple)
    uncategorized_expense_count: int = 0
    uncategorized_expense_amount: Decimal = Decimal("0")
    savings_goals: tuple[SavingsGoalStatus, ...] = field(default_factory=tuple)
    reference_snapshot_age_days: int | None = None
    reference_snapshot_max_age_days: int = 548  # ~18 months
    has_any_categories: bool = True
    has_any_budgets: bool = True
