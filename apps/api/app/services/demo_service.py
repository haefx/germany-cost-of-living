"""Demo households: a real user account with no email/password login, seeded
with realistic-but-synthetic data and auto-expired after a fixed TTL.

Demo and real accounts share every code path after provisioning — there is
no ``if is_demo`` branching anywhere in the finance CRUD, insights, or
export logic. The only demo-specific code is here (creation) and in the
expiry job.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models.finance import (
    Budget,
    Category,
    ExpenseEntry,
    IncomeEntry,
    IncomeSource,
    RecurrenceFrequency,
    RecurrenceRule,
    SavingsGoal,
    SavingsGoalContribution,
)
from ..models.user import User
from ..security.password import password_helper

settings = get_settings()


async def _global_category_id(session: AsyncSession, name: str) -> uuid.UUID:
    result = await session.execute(
        select(Category.id).where(Category.name == name, Category.user_id.is_(None))
    )
    return result.scalar_one()


async def provision_demo_user(session: AsyncSession) -> User:
    now = datetime.now(UTC)
    user_db: SQLAlchemyUserDatabase[User, uuid.UUID] = SQLAlchemyUserDatabase(session, User)
    user = await user_db.create(
        {
            "email": f"demo-{uuid.uuid4().hex}@demo.internal",
            "hashed_password": password_helper.hash(uuid.uuid4().hex),
            "is_active": True,
            "is_verified": True,
            "is_demo": True,
            "demo_expires_at": now + timedelta(hours=settings.demo_household_ttl_hours),
        }
    )
    await _seed_demo_household(session, user.id)
    return user


async def _seed_demo_household(session: AsyncSession, user_id: uuid.UUID) -> None:
    today = date.today()
    month_start = today.replace(day=1)

    salary = await _global_category_id(session, "Gehalt")
    housing = await _global_category_id(session, "Miete & Wohnen")
    groceries = await _global_category_id(session, "Lebensmittel")
    utilities = await _global_category_id(session, "Nebenkosten")
    subscriptions = await _global_category_id(session, "Abos")
    leisure = await _global_category_id(session, "Freizeit")
    savings = await _global_category_id(session, "Sparen")

    monthly_rule = RecurrenceRule(
        user_id=user_id,
        frequency=RecurrenceFrequency.MONTHLY,
        interval_count=1,
        start_date=month_start,
    )
    session.add(monthly_rule)
    await session.flush()

    session.add(
        IncomeEntry(
            user_id=user_id,
            category_id=salary,
            label="Gehalt (Demo)",
            amount=Decimal("3450.00"),
            entry_date=month_start,
            is_recurring=True,
            recurrence_rule_id=monthly_rule.id,
            source=IncomeSource.MANUAL,
        )
    )

    demo_expenses = [
        (housing, "Miete", Decimal("1050.00")),
        (utilities, "Nebenkosten", Decimal("150.00")),
        (groceries, "Lebensmittel", Decimal("320.00")),
        (subscriptions, "Streaming-Abo", Decimal("65.00")),
        (leisure, "Fitnessstudio", Decimal("35.00")),
        (savings, "ETF-Sparplan", Decimal("75.00")),
    ]
    savings_expense: ExpenseEntry | None = None
    for category_id, label, amount in demo_expenses:
        expense = ExpenseEntry(
            user_id=user_id,
            category_id=category_id,
            label=label,
            amount=amount,
            entry_date=month_start,
            is_recurring=True,
            recurrence_rule_id=monthly_rule.id,
        )
        session.add(expense)
        if category_id == savings:
            savings_expense = expense

    session.add(
        Budget(
            user_id=user_id,
            category_id=groceries,
            monthly_limit=Decimal("350.00"),
            effective_from=month_start,
        )
    )

    await session.flush()
    goal = SavingsGoal(
        user_id=user_id,
        name="ETF-Vermögensaufbau",
        target_amount=Decimal("50000.00"),
        target_date=today.replace(year=today.year + 10),
        template_key="global_equity",
        annual_return_min_pct=Decimal("4.00"),
        annual_return_max_pct=Decimal("7.00"),
        monthly_contribution=Decimal("75.00"),
        contribution_start_date=month_start,
        linked_expense_id=savings_expense.id if savings_expense else None,
        category_id=savings,
    )
    session.add(goal)
    await session.flush()
    session.add(
        SavingsGoalContribution(
            savings_goal_id=goal.id, amount=Decimal("250.00"), contributed_on=month_start
        )
    )
    await session.flush()


async def expire_demo_users(session: AsyncSession) -> int:
    """Deletes every demo user whose TTL has passed. Cascades remove all of
    their data via the ``ON DELETE CASCADE`` foreign keys. Real accounts
    (``is_demo=False``) are never touched by this query.
    """
    now = datetime.now(UTC)
    result = await session.execute(
        select(User).where(User.is_demo.is_(True), User.demo_expires_at < now)
    )
    expired_users = list(result.scalars().all())
    for user in expired_users:
        await session.delete(user)
    await session.flush()
    return len(expired_users)
