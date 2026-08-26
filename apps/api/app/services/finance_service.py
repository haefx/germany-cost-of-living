"""Orchestrates income, expense, budget, and savings-goal operations.

Routers call exactly one function here per request; this is the only layer
that combines multiple repositories (e.g. creating a recurrence rule before
the entry that references it) or calls into ``packages/analytics`` for
computed values (budget remaining, savings-goal progress).
"""

from __future__ import annotations

import math
import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from analytics.recurrence import add_months

from ..models.finance import Budget, ExpenseEntry, IncomeEntry, SavingsGoal
from ..repositories.category import CategoryRepository
from ..repositories.finance import (
    BudgetRepository,
    ExpenseRepository,
    IncomeRepository,
    RecurrenceRuleRepository,
    SavingsGoalContributionRepository,
    SavingsGoalRepository,
    month_bounds,
)
from ..schemas.finance import (
    BudgetCreate,
    BudgetRead,
    BudgetStatusRead,
    BudgetUpdate,
    ExpenseEntryCreate,
    ExpenseEntryUpdate,
    IncomeEntryCreate,
    IncomeEntryUpdate,
    SavingsGoalContributionCreate,
    SavingsGoalCreate,
    SavingsGoalProgressRead,
    SavingsGoalRead,
    SavingsGoalUpdate,
)


class EntryNotFoundError(Exception):
    pass


class BudgetNotFoundError(Exception):
    pass


class SavingsGoalNotFoundError(Exception):
    pass


class ContributionNotFoundError(Exception):
    pass


class LinkedExpenseNotFoundError(Exception):
    pass


class RecurrenceRequiredError(Exception):
    pass


# --- Income ---


async def create_income_entry(
    income_repo: IncomeRepository,
    rule_repo: RecurrenceRuleRepository,
    user_id: uuid.UUID,
    data: IncomeEntryCreate,
) -> IncomeEntry:
    recurrence_rule_id = None
    if data.recurrence is not None:
        rule = await rule_repo.create(user_id, **data.recurrence.model_dump())
        recurrence_rule_id = rule.id
    fields = data.model_dump(exclude={"recurrence"})
    return await income_repo.create(user_id, recurrence_rule_id=recurrence_rule_id, **fields)


async def update_income_entry(
    income_repo: IncomeRepository, user_id: uuid.UUID, entry_id: uuid.UUID, data: IncomeEntryUpdate
) -> IncomeEntry:
    updated = await income_repo.update(user_id, entry_id, **data.model_dump(exclude_unset=True))
    if updated is None:
        raise EntryNotFoundError
    return updated


async def delete_income_entry(
    income_repo: IncomeRepository, user_id: uuid.UUID, entry_id: uuid.UUID
) -> None:
    if not await income_repo.delete(user_id, entry_id):
        raise EntryNotFoundError


# --- Expenses ---


async def create_expense_entry(
    expense_repo: ExpenseRepository,
    rule_repo: RecurrenceRuleRepository,
    user_id: uuid.UUID,
    data: ExpenseEntryCreate,
) -> ExpenseEntry:
    recurrence_rule_id = None
    if data.recurrence is not None:
        rule = await rule_repo.create(user_id, **data.recurrence.model_dump())
        recurrence_rule_id = rule.id
    fields = data.model_dump(exclude={"recurrence"})
    return await expense_repo.create(user_id, recurrence_rule_id=recurrence_rule_id, **fields)


async def update_expense_entry(
    expense_repo: ExpenseRepository,
    rule_repo: RecurrenceRuleRepository,
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    data: ExpenseEntryUpdate,
) -> ExpenseEntry:
    entry = await expense_repo.get(user_id, entry_id)
    if entry is None:
        raise EntryNotFoundError

    old_rule_id = entry.recurrence_rule_id
    fields = data.model_dump(exclude_unset=True, exclude={"recurrence"})
    requested_recurring = fields.get("is_recurring", entry.is_recurring)

    if data.recurrence is not None:
        rule = await rule_repo.create(user_id, **data.recurrence.model_dump())
        fields["recurrence_rule_id"] = rule.id
        fields["is_recurring"] = True
    elif requested_recurring:
        if old_rule_id is None:
            raise RecurrenceRequiredError
    else:
        fields["recurrence_rule_id"] = None

    updated = await expense_repo.update(user_id, entry_id, **fields)
    if updated is None:
        raise EntryNotFoundError

    if old_rule_id is not None and old_rule_id != updated.recurrence_rule_id:
        await rule_repo.delete(user_id, old_rule_id)
    return updated


async def delete_expense_entry(
    expense_repo: ExpenseRepository, user_id: uuid.UUID, entry_id: uuid.UUID
) -> None:
    if not await expense_repo.delete(user_id, entry_id):
        raise EntryNotFoundError


# --- Budgets ---


async def create_budget(
    budget_repo: BudgetRepository, user_id: uuid.UUID, data: BudgetCreate
) -> Budget:
    return await budget_repo.create(user_id, **data.model_dump())


async def update_budget(
    budget_repo: BudgetRepository, user_id: uuid.UUID, budget_id: uuid.UUID, data: BudgetUpdate
) -> Budget:
    updated = await budget_repo.update(user_id, budget_id, **data.model_dump(exclude_unset=True))
    if updated is None:
        raise BudgetNotFoundError
    return updated


async def delete_budget(
    budget_repo: BudgetRepository, user_id: uuid.UUID, budget_id: uuid.UUID
) -> None:
    if not await budget_repo.delete(user_id, budget_id):
        raise BudgetNotFoundError


async def _budget_status(
    expense_repo: ExpenseRepository,
    category_repo: CategoryRepository,
    budget: Budget,
    month: date,
) -> BudgetStatusRead:
    entries = await expense_repo.list_for_category_and_month(
        budget.user_id, budget.category_id, month
    )
    actual_spent = sum((entry.amount for entry in entries), Decimal("0.00"))
    category = await category_repo.get_visible(budget.user_id, budget.category_id)
    return BudgetStatusRead(
        budget=BudgetRead.model_validate(budget),
        category_name=category.name if category else "",
        month=month_bounds(month)[0],
        actual_spent=actual_spent,
        remaining=budget.monthly_limit - actual_spent,
        is_over_budget=actual_spent > budget.monthly_limit,
    )


async def list_budget_statuses(
    budget_repo: BudgetRepository,
    expense_repo: ExpenseRepository,
    category_repo: CategoryRepository,
    user_id: uuid.UUID,
    month: date,
) -> list[BudgetStatusRead]:
    budgets = await budget_repo.list_active_for_month(user_id, month)
    return [await _budget_status(expense_repo, category_repo, budget, month) for budget in budgets]


# --- Savings goals ---


async def create_savings_goal(
    goal_repo: SavingsGoalRepository,
    expense_repo: ExpenseRepository,
    user_id: uuid.UUID,
    data: SavingsGoalCreate,
) -> SavingsGoal:
    if (
        data.linked_expense_id is not None
        and await expense_repo.get(user_id, data.linked_expense_id) is None
    ):
        raise LinkedExpenseNotFoundError
    return await goal_repo.create(user_id, **data.model_dump())


async def update_savings_goal(
    goal_repo: SavingsGoalRepository,
    user_id: uuid.UUID,
    goal_id: uuid.UUID,
    data: SavingsGoalUpdate,
) -> SavingsGoal:
    updated = await goal_repo.update(user_id, goal_id, **data.model_dump(exclude_unset=True))
    if updated is None:
        raise SavingsGoalNotFoundError
    return updated


async def delete_savings_goal(
    goal_repo: SavingsGoalRepository, user_id: uuid.UUID, goal_id: uuid.UUID
) -> None:
    if not await goal_repo.delete(user_id, goal_id):
        raise SavingsGoalNotFoundError


def _months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month)


def _project_completion_date(
    goal: SavingsGoal, contributions: list[Any], current_amount: Decimal
) -> date | None:
    if current_amount >= goal.target_amount:
        return max((c.contributed_on for c in contributions), default=date.today())
    if goal.monthly_contribution:
        avg_monthly_rate = goal.monthly_contribution
    elif contributions:
        first_contribution_date = min(c.contributed_on for c in contributions)
        months_elapsed = max(1, _months_between(first_contribution_date, date.today()))
        avg_monthly_rate = current_amount / months_elapsed
    else:
        return None
    if avg_monthly_rate <= 0:
        return None

    remaining = goal.target_amount - current_amount
    months_needed = math.ceil(remaining / avg_monthly_rate)
    return add_months(date.today(), months_needed)


async def goal_progress(
    contribution_repo: SavingsGoalContributionRepository, goal: SavingsGoal
) -> SavingsGoalProgressRead:
    contributions = await contribution_repo.list_for_goal(goal.user_id, goal.id)
    special_contributions = sum((c.amount for c in contributions), Decimal("0.00"))
    scheduled_contributions = Decimal("0.00")
    if goal.monthly_contribution and goal.contribution_start_date:
        completed_months = (
            0
            if goal.contribution_start_date > date.today()
            else _months_between(goal.contribution_start_date, date.today()) + 1
        )
        scheduled_contributions = goal.monthly_contribution * completed_months
    current_amount = special_contributions + scheduled_contributions
    progress_pct = (
        (current_amount / goal.target_amount * 100) if goal.target_amount > 0 else Decimal("0")
    )
    return SavingsGoalProgressRead(
        goal=SavingsGoalRead.model_validate(goal),
        current_amount=current_amount,
        progress_pct=progress_pct.quantize(Decimal("0.1")),
        projected_completion_date=_project_completion_date(goal, contributions, current_amount),
    )


async def add_contribution(
    contribution_repo: SavingsGoalContributionRepository,
    user_id: uuid.UUID,
    goal_id: uuid.UUID,
    data: SavingsGoalContributionCreate,
) -> Any:
    contribution = await contribution_repo.create_for_goal(user_id, goal_id, **data.model_dump())
    if contribution is None:
        raise SavingsGoalNotFoundError
    return contribution


async def delete_contribution(
    contribution_repo: SavingsGoalContributionRepository,
    user_id: uuid.UUID,
    goal_id: uuid.UUID,
    contribution_id: uuid.UUID,
) -> None:
    if not await contribution_repo.delete_for_goal(user_id, goal_id, contribution_id):
        raise ContributionNotFoundError
