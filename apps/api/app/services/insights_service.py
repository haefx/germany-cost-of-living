"""Assembles an ``InsightContext`` from real database rows.

This is the only place that translates household data into the shape the
deterministic insights engine (packages/analytics) expects — the engine
itself never queries a database, which is what keeps its rules
independently unit-testable.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from analytics.insights.models import (
    BudgetStatus,
    CategorySpending,
    InsightContext,
    RecurringExpenseEntry,
    SavingsGoalStatus,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.category import CategoryRepository
from ..repositories.finance import (
    BudgetRepository,
    ExpenseRepository,
    IncomeRepository,
    SavingsGoalContributionRepository,
    SavingsGoalRepository,
)
from ..services.city_service import DATA_SOURCE_KEY, get_data_source_statuses

TRAILING_MONTHS = 3
HOUSING_CATEGORY_NAME = "Miete & Wohnen"


def _sum_amounts(entries: list) -> Decimal:
    return sum((entry.amount for entry in entries), Decimal("0.00"))


def _previous_months(month: date, count: int) -> list[date]:
    months = []
    year, mon = month.year, month.month
    for _ in range(count):
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
        months.append(date(year, mon, 1))
    return months


def _months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month)


async def build_insight_context(
    session: AsyncSession,
    user_id: uuid.UUID,
    month: date,
    income_repo: IncomeRepository,
    expense_repo: ExpenseRepository,
    budget_repo: BudgetRepository,
    category_repo: CategoryRepository,
    goal_repo: SavingsGoalRepository,
    contribution_repo: SavingsGoalContributionRepository,
) -> InsightContext:
    trailing_months = _previous_months(month, TRAILING_MONTHS)

    current_income_entries = await income_repo.list_for_month(user_id, month)
    current_expense_entries = await expense_repo.list_for_month(user_id, month)
    total_income = _sum_amounts(current_income_entries)
    total_expenses = _sum_amounts(current_expense_entries)

    trailing_expense_entries_by_month = [
        await expense_repo.list_for_month(user_id, m) for m in trailing_months
    ]
    trailing_total_expenses = tuple(
        _sum_amounts(entries) for entries in trailing_expense_entries_by_month
    )

    categories = await category_repo.list_visible(user_id)
    category_names = {category.id: category.name for category in categories}

    relevant_category_ids = {
        entry.category_id for entry in current_expense_entries if entry.category_id
    }
    for entries in trailing_expense_entries_by_month:
        relevant_category_ids.update(entry.category_id for entry in entries if entry.category_id)

    category_spending = []
    for category_id in relevant_category_ids:
        current_amount = _sum_amounts(
            [e for e in current_expense_entries if e.category_id == category_id]
        )
        trailing_history = tuple(
            _sum_amounts([e for e in entries if e.category_id == category_id])
            for entries in trailing_expense_entries_by_month
        )
        trailing_average = (
            sum(trailing_history, Decimal("0.00")) / len(trailing_history)
            if trailing_history
            else Decimal("0.00")
        )
        category_spending.append(
            CategorySpending(
                category_id=str(category_id),
                category_name=category_names.get(category_id, ""),
                current_amount=current_amount,
                trailing_average=trailing_average,
                trailing_history=trailing_history,
            )
        )

    active_budgets = await budget_repo.list_active_for_month(user_id, month)
    budget_statuses = [
        BudgetStatus(
            category_id=str(budget.category_id),
            category_name=category_names.get(budget.category_id, ""),
            monthly_limit=budget.monthly_limit,
            actual_spent=_sum_amounts(
                [e for e in current_expense_entries if e.category_id == budget.category_id]
            ),
        )
        for budget in active_budgets
    ]

    all_expenses = await expense_repo.list(user_id)
    recurring_expenses = tuple(
        RecurringExpenseEntry(
            id=str(entry.id),
            category_id=str(entry.category_id) if entry.category_id else None,
            label=entry.label,
            amount=entry.amount,
            entry_date=entry.entry_date,
            recurrence_rule_id=str(entry.recurrence_rule_id),
        )
        for entry in all_expenses
        if entry.is_recurring and entry.recurrence_rule_id
    )

    uncategorized_entries = [e for e in current_expense_entries if e.category_id is None]

    goals = await goal_repo.list(user_id)
    savings_goal_statuses = []
    for goal in goals:
        contributions = await contribution_repo.list_for_goal(user_id, goal.id)
        current_amount = _sum_amounts(contributions)
        if contributions:
            first_contribution_date = min(c.contributed_on for c in contributions)
            months_elapsed = max(1, _months_between(first_contribution_date, month))
            trailing_avg = current_amount / months_elapsed
        else:
            trailing_avg = Decimal("0.00")
        savings_goal_statuses.append(
            SavingsGoalStatus(
                id=str(goal.id),
                name=goal.name,
                target_amount=goal.target_amount,
                current_amount=current_amount,
                target_date=goal.target_date,
                trailing_monthly_contribution_avg=trailing_avg,
            )
        )

    housing_category_id = next(
        (c.id for c in categories if c.name == HOUSING_CATEGORY_NAME), None
    )
    rent_amount = (
        _sum_amounts([e for e in current_expense_entries if e.category_id == housing_category_id])
        if housing_category_id
        else None
    )

    data_source_statuses = await get_data_source_statuses(session)
    reference_status = next(
        (s for s in data_source_statuses if s.key == DATA_SOURCE_KEY), None
    )

    has_any_budgets = len(await budget_repo.list(user_id)) > 0

    return InsightContext(
        month=month,
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=total_income if total_income > 0 else None,
        rent_amount=rent_amount,
        category_spending=tuple(category_spending),
        trailing_total_expenses=trailing_total_expenses,
        budgets=tuple(budget_statuses),
        recurring_expenses=recurring_expenses,
        uncategorized_expense_count=len(uncategorized_entries),
        uncategorized_expense_amount=_sum_amounts(uncategorized_entries),
        savings_goals=tuple(savings_goal_statuses),
        reference_snapshot_age_days=reference_status.age_days if reference_status else None,
        has_any_categories=True,
        has_any_budgets=has_any_budgets,
    )
