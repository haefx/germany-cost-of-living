"""Request/response schemas for the personal finance domain."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models.finance import CategoryKind, IncomeSource, RecurrenceFrequency


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: CategoryKind
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(default=None, max_length=50)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(default=None, max_length=50)
    is_archived: bool | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    name: str
    kind: CategoryKind
    color: str
    icon: str | None
    is_archived: bool


class RecurrenceRuleCreate(BaseModel):
    frequency: RecurrenceFrequency
    interval_count: int = Field(default=1, ge=1, le=52)
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def _end_after_start(self) -> RecurrenceRuleCreate:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class RecurrenceRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    frequency: RecurrenceFrequency
    interval_count: int
    start_date: date
    end_date: date | None


class IncomeEntryCreate(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2)
    entry_date: date
    category_id: uuid.UUID | None = None
    is_recurring: bool = False
    recurrence: RecurrenceRuleCreate | None = None
    source: IncomeSource = IncomeSource.MANUAL
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def _recurrence_required_if_recurring(self) -> IncomeEntryCreate:
        if self.is_recurring and self.recurrence is None:
            raise ValueError("recurrence is required when is_recurring is true")
        return self


class IncomeEntryUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    entry_date: date | None = None
    category_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class IncomeEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    amount: Decimal
    entry_date: date
    category_id: uuid.UUID | None
    is_recurring: bool
    recurrence_rule_id: uuid.UUID | None
    source: IncomeSource
    notes: str | None


class ExpenseEntryCreate(BaseModel):
    label: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2)
    entry_date: date
    category_id: uuid.UUID | None = None
    is_recurring: bool = False
    recurrence: RecurrenceRuleCreate | None = None
    merchant: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    is_planned: bool = False
    budget_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _recurrence_required_if_recurring(self) -> ExpenseEntryCreate:
        if self.is_recurring and self.recurrence is None:
            raise ValueError("recurrence is required when is_recurring is true")
        return self


class ExpenseEntryUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    entry_date: date | None = None
    category_id: uuid.UUID | None = None
    is_recurring: bool | None = None
    recurrence: RecurrenceRuleCreate | None = None
    merchant: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    is_planned: bool | None = None
    budget_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _recurrence_not_allowed_when_disabled(self) -> ExpenseEntryUpdate:
        if self.is_recurring is False and self.recurrence is not None:
            raise ValueError("recurrence must be null when is_recurring is false")
        return self


class ExpenseEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    amount: Decimal
    entry_date: date
    source_amount: Decimal | None = None
    source_entry_date: date | None = None
    category_id: uuid.UUID | None
    is_recurring: bool
    recurrence_rule_id: uuid.UUID | None
    recurrence: RecurrenceRuleRead | None = None
    merchant: str | None
    notes: str | None
    is_planned: bool
    budget_id: uuid.UUID | None


class BudgetCreate(BaseModel):
    category_id: uuid.UUID
    monthly_limit: Decimal = Field(gt=0, decimal_places=2)
    effective_from: date
    effective_to: date | None = None


class BudgetUpdate(BaseModel):
    monthly_limit: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    effective_to: date | None = None


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    monthly_limit: Decimal
    effective_from: date
    effective_to: date | None


class BudgetStatusRead(BaseModel):
    budget: BudgetRead
    category_name: str
    month: date
    actual_spent: Decimal
    remaining: Decimal
    is_over_budget: bool


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    target_amount: Decimal = Field(gt=0, decimal_places=2)
    target_date: date | None = None
    category_id: uuid.UUID | None = None
    template_key: str | None = Field(default=None, max_length=50)
    annual_return_min_pct: Decimal | None = Field(default=None, ge=0, le=30)
    annual_return_max_pct: Decimal | None = Field(default=None, ge=0, le=30)
    monthly_contribution: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    contribution_start_date: date | None = None
    linked_expense_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _valid_return_range(self) -> SavingsGoalCreate:
        if (
            self.annual_return_min_pct is not None
            and self.annual_return_max_pct is not None
            and self.annual_return_min_pct > self.annual_return_max_pct
        ):
            raise ValueError("annual_return_min_pct must not exceed annual_return_max_pct")
        return self


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    target_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    target_date: date | None = None
    archived_at: date | None = None
    template_key: str | None = Field(default=None, max_length=50)
    annual_return_min_pct: Decimal | None = Field(default=None, ge=0, le=30)
    annual_return_max_pct: Decimal | None = Field(default=None, ge=0, le=30)
    monthly_contribution: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    contribution_start_date: date | None = None

    @model_validator(mode="after")
    def _valid_return_range(self) -> SavingsGoalUpdate:
        if (
            self.annual_return_min_pct is not None
            and self.annual_return_max_pct is not None
            and self.annual_return_min_pct > self.annual_return_max_pct
        ):
            raise ValueError("annual_return_min_pct must not exceed annual_return_max_pct")
        return self


class SavingsGoalContributionCreate(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    contributed_on: date
    note: str | None = Field(default=None, max_length=500)


class SavingsGoalContributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: Decimal
    contributed_on: date
    note: str | None


class SavingsGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    target_amount: Decimal
    target_date: date | None
    template_key: str | None
    annual_return_min_pct: Decimal | None
    annual_return_max_pct: Decimal | None
    monthly_contribution: Decimal | None
    contribution_start_date: date | None
    linked_expense_id: uuid.UUID | None
    category_id: uuid.UUID | None
    archived_at: date | None


class SavingsGoalProgressRead(BaseModel):
    goal: SavingsGoalRead
    current_amount: Decimal
    progress_pct: Decimal
    projected_completion_date: date | None
