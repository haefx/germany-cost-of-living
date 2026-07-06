"""Shared FastAPI dependencies: the current user and repository factories."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .models.user import User
from .repositories.category import CategoryRepository
from .repositories.finance import (
    BudgetRepository,
    ExpenseRepository,
    IncomeRepository,
    RecurrenceRuleRepository,
    SavingsGoalContributionRepository,
    SavingsGoalRepository,
)
from .security.users import current_active_user

CurrentUser = Annotated[User, Depends(current_active_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]


def get_category_repository(session: DbSession) -> CategoryRepository:
    return CategoryRepository(session)


def get_income_repository(session: DbSession) -> IncomeRepository:
    return IncomeRepository(session)


def get_expense_repository(session: DbSession) -> ExpenseRepository:
    return ExpenseRepository(session)


def get_recurrence_rule_repository(session: DbSession) -> RecurrenceRuleRepository:
    return RecurrenceRuleRepository(session)


def get_budget_repository(session: DbSession) -> BudgetRepository:
    return BudgetRepository(session)


def get_savings_goal_repository(session: DbSession) -> SavingsGoalRepository:
    return SavingsGoalRepository(session)


def get_savings_goal_contribution_repository(
    session: DbSession,
) -> SavingsGoalContributionRepository:
    return SavingsGoalContributionRepository(session)
