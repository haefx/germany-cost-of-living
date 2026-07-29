"""Repositories for income, expenses, recurrence rules, budgets, and savings
goals — all built on ``UserOwnedRepository``.

Monthly aggregation (``list_for_month``) expands the associated recurrence
rule and returns one monthly aggregate row. Weekly entries are multiplied by
their actual occurrences in the month; monthly and yearly rules only appear
in months in which they occur.
"""

from __future__ import annotations

import uuid
from calendar import monthrange
from datetime import date
from types import SimpleNamespace
from typing import Any

from analytics.recurrence import RecurrenceRule as AnalyticsRecurrenceRule
from analytics.recurrence import expand_occurrences
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.finance import (
    Budget,
    ExpenseEntry,
    IncomeEntry,
    RecurrenceRule,
    SavingsGoal,
    SavingsGoalContribution,
)
from .base import UserOwnedRepository


def month_bounds(month: date) -> tuple[date, date]:
    start = month.replace(day=1)
    end = month.replace(day=monthrange(month.year, month.month)[1])
    return start, end


def _to_analytics_rule(rule: RecurrenceRule) -> AnalyticsRecurrenceRule:
    return AnalyticsRecurrenceRule(
        frequency=rule.frequency.value,
        interval_count=rule.interval_count,
        start_date=rule.start_date,
        end_date=rule.end_date,
    )


async def _list_entries_for_month(
    session: AsyncSession, model: Any, user_id: uuid.UUID, month: date
) -> list[Any]:
    start, end = month_bounds(month)

    direct_result = await session.execute(
        select(model).where(
            model.user_id == user_id,
            model.is_recurring.is_(False),
            model.entry_date >= start,
            model.entry_date <= end,
        )
    )
    direct_entries: list[Any] = list(direct_result.scalars().all())

    recurring_result = await session.execute(
        select(model, RecurrenceRule)
        .join(RecurrenceRule, model.recurrence_rule_id == RecurrenceRule.id)
        .where(
            model.user_id == user_id,
            model.is_recurring.is_(True),
            model.entry_date <= end,
        )
    )
    for entry, rule in recurring_result.all():
        occurrences = expand_occurrences(_to_analytics_rule(rule), start, end)
        if occurrences:
            monthly_entry = SimpleNamespace(
                **{column.key: getattr(entry, column.key) for column in sa_inspect(model).columns}
            )
            monthly_entry.amount = entry.amount * len(occurrences)
            monthly_entry.entry_date = occurrences[0]
            direct_entries.append(monthly_entry)

    return direct_entries


class IncomeRepository(UserOwnedRepository[IncomeEntry]):
    model = IncomeEntry

    async def list_for_month(self, user_id: uuid.UUID, month: date) -> list[IncomeEntry]:
        return await _list_entries_for_month(self.session, IncomeEntry, user_id, month)


class ExpenseRepository(UserOwnedRepository[ExpenseEntry]):
    model = ExpenseEntry

    async def list_for_month(self, user_id: uuid.UUID, month: date) -> list[ExpenseEntry]:
        return await _list_entries_for_month(self.session, ExpenseEntry, user_id, month)

    async def list_for_category_and_month(
        self, user_id: uuid.UUID, category_id: uuid.UUID, month: date
    ) -> list[ExpenseEntry]:
        entries = await self.list_for_month(user_id, month)
        return [entry for entry in entries if entry.category_id == category_id]


class RecurrenceRuleRepository(UserOwnedRepository[RecurrenceRule]):
    model = RecurrenceRule


class BudgetRepository(UserOwnedRepository[Budget]):
    model = Budget

    async def list_active_for_month(self, user_id: uuid.UUID, month: date) -> list[Budget]:
        start, _ = month_bounds(month)
        result = await self.session.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.effective_from <= start,
                (Budget.effective_to.is_(None)) | (Budget.effective_to >= start),
            )
        )
        return list(result.scalars().all())


class SavingsGoalRepository(UserOwnedRepository[SavingsGoal]):
    model = SavingsGoal


class SavingsGoalContributionRepository:
    """Contributions are owned indirectly through their savings goal (the
    table has no ``user_id`` column of its own), so this repository is not
    built on ``UserOwnedRepository`` — every method verifies goal ownership
    via a join instead.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_goal(
        self, user_id: uuid.UUID, savings_goal_id: uuid.UUID
    ) -> list[SavingsGoalContribution]:
        result = await self.session.execute(
            select(SavingsGoalContribution)
            .join(SavingsGoal, SavingsGoalContribution.savings_goal_id == SavingsGoal.id)
            .where(SavingsGoal.id == savings_goal_id, SavingsGoal.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create_for_goal(
        self, user_id: uuid.UUID, savings_goal_id: uuid.UUID, **fields: Any
    ) -> SavingsGoalContribution | None:
        goal_result = await self.session.execute(
            select(SavingsGoal.id).where(
                SavingsGoal.id == savings_goal_id, SavingsGoal.user_id == user_id
            )
        )
        if goal_result.scalar_one_or_none() is None:
            return None
        contribution = SavingsGoalContribution(savings_goal_id=savings_goal_id, **fields)
        self.session.add(contribution)
        await self.session.flush()
        return contribution

    async def delete_for_goal(
        self, user_id: uuid.UUID, savings_goal_id: uuid.UUID, contribution_id: uuid.UUID
    ) -> bool:
        contributions = await self.list_for_goal(user_id, savings_goal_id)
        target = next((c for c in contributions if c.id == contribution_id), None)
        if target is None:
            return False
        await self.session.delete(target)
        await self.session.flush()
        return True
