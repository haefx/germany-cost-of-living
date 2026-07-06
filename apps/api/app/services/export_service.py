"""CSV and JSON export of a user's own data.

CSV cells are sanitized against formula injection: a cell whose text starts
with ``=``, ``+``, ``-``, or ``@`` is prefixed with a single quote before
Excel/Sheets would otherwise interpret it as a formula when the file is
reopened.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.finance import (
    Budget,
    Category,
    ExpenseEntry,
    IncomeEntry,
    RecurrenceRule,
    SavingsGoal,
    SavingsGoalContribution,
)
from ..models.user import User

_FORMULA_PREFIXES = ("=", "+", "-", "@")

CategoryNames = dict[uuid.UUID | None, str]


def _sanitize_cell(value: str) -> str:
    if value and value[0] in _FORMULA_PREFIXES:
        return "'" + value
    return value


def income_entries_to_csv(entries: list[IncomeEntry], category_names: CategoryNames) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["label", "amount", "entry_date", "category", "notes"])
    for entry in entries:
        writer.writerow(
            [
                _sanitize_cell(entry.label),
                str(entry.amount),
                entry.entry_date.isoformat(),
                _sanitize_cell(category_names.get(entry.category_id, "")),
                _sanitize_cell(entry.notes or ""),
            ]
        )
    return output.getvalue()


def expense_entries_to_csv(entries: list[ExpenseEntry], category_names: CategoryNames) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["label", "amount", "entry_date", "category", "merchant", "notes"])
    for entry in entries:
        writer.writerow(
            [
                _sanitize_cell(entry.label),
                str(entry.amount),
                entry.entry_date.isoformat(),
                _sanitize_cell(category_names.get(entry.category_id, "")),
                _sanitize_cell(entry.merchant or ""),
                _sanitize_cell(entry.notes or ""),
            ]
        )
    return output.getvalue()


def _entry_to_dict(entry: Any) -> dict[str, Any]:
    return {
        column.name: getattr(entry, column.name)
        for column in entry.__table__.columns
        if column.name != "user_id"
    }


async def export_account_data(session: AsyncSession, user: User) -> dict[str, Any]:
    """Every entity the user owns, as plain JSON-serializable dicts. Deliberately
    excludes ``hashed_password`` and any session/access-token rows.
    """

    async def _all(model: Any) -> list[dict[str, Any]]:
        result = await session.execute(select(model).where(model.user_id == user.id))
        return [_entry_to_dict(row) for row in result.scalars().all()]

    goal_result = await session.execute(select(SavingsGoal).where(SavingsGoal.user_id == user.id))
    goals = list(goal_result.scalars().all())
    goal_ids = [goal.id for goal in goals]
    contributions: list[dict[str, Any]] = []
    if goal_ids:
        contribution_result = await session.execute(
            select(SavingsGoalContribution).where(
                SavingsGoalContribution.savings_goal_id.in_(goal_ids)
            )
        )
        contributions = [_entry_to_dict(row) for row in contribution_result.scalars().all()]

    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "account": {
            "email": user.email,
            "is_demo": user.is_demo,
        },
        "categories": await _all(Category),
        "recurrence_rules": await _all(RecurrenceRule),
        "income_entries": await _all(IncomeEntry),
        "expense_entries": await _all(ExpenseEntry),
        "budgets": await _all(Budget),
        "savings_goals": [_entry_to_dict(goal) for goal in goals],
        "savings_goal_contributions": contributions,
    }
