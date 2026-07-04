"""Personal household finance schema: categories, recurring rules, income and
expense entries, budgets, and savings goals.

Every row that belongs to a specific user carries a ``user_id`` foreign key
with ``ondelete="CASCADE"``, so deleting a user (real or expired demo)
removes all of their data in one statement without orphaned rows.

Recurring income/expenses store the *rule* only (frequency, interval,
start/end date) — occurrence dates for a reporting window are computed on
demand by ``packages/analytics/analytics/recurrence.py``, never
materialized as rows.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CategoryKind(enum.StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class RecurrenceFrequency(enum.StrEnum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class IncomeSource(enum.StrEnum):
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    GROSS_NET_ESTIMATE = "gross_net_estimate"


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A spending/income category. ``user_id`` is NULL for the global default
    categories seeded once by migration, and set for user-created custom
    categories.
    """

    __tablename__ = "category"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    kind: Mapped[CategoryKind] = mapped_column(
        Enum(CategoryKind, name="category_kind"), nullable=False
    )
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#3B82F6")
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)


class RecurrenceRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recurrence_rule"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    frequency: Mapped[RecurrenceFrequency] = mapped_column(
        Enum(RecurrenceFrequency, name="recurrence_frequency"), nullable=False
    )
    interval_count: Mapped[int] = mapped_column(default=1, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class IncomeEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "income_entry"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(default=False, nullable=False)
    recurrence_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recurrence_rule.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[IncomeSource] = mapped_column(
        Enum(IncomeSource, name="income_source"), default=IncomeSource.MANUAL, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ExpenseEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "expense_entry"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    # Nullable on purpose: uncategorized expenses are a real state the
    # missing_categories insight rule needs to detect, not an input error.
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(default=False, nullable=False)
    recurrence_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recurrence_rule.id", ondelete="SET NULL"), nullable=True
    )
    merchant: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_planned: Mapped[bool] = mapped_column(default=False, nullable=False)
    budget_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("budget.id", ondelete="SET NULL"), nullable=True
    )


class Budget(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "budget"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id", ondelete="CASCADE"), nullable=False
    )
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class SavingsGoal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "savings_goal"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    archived_at: Mapped[date | None] = mapped_column(Date, nullable=True)


class SavingsGoalContribution(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A contribution ledger rather than a single running total, so real
    contribution velocity can be computed for the savings_goal_delay insight
    and for the progress chart.
    """

    __tablename__ = "savings_goal_contribution"

    savings_goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("savings_goal.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    contributed_on: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
