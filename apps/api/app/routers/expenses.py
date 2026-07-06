"""Expense entry endpoints."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import CurrentUser, get_expense_repository, get_recurrence_rule_repository
from ..repositories.finance import ExpenseRepository, RecurrenceRuleRepository
from ..schemas.finance import ExpenseEntryCreate, ExpenseEntryRead, ExpenseEntryUpdate
from ..services import finance_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseEntryRead])
async def list_expenses(
    user: CurrentUser,
    month: date | None = None,
    repo: ExpenseRepository = Depends(get_expense_repository),
) -> list[ExpenseEntryRead]:
    entries = await repo.list_for_month(user.id, month) if month else await repo.list(user.id)
    return [ExpenseEntryRead.model_validate(entry) for entry in entries]


@router.post("", response_model=ExpenseEntryRead, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseEntryCreate,
    user: CurrentUser,
    repo: ExpenseRepository = Depends(get_expense_repository),
    rule_repo: RecurrenceRuleRepository = Depends(get_recurrence_rule_repository),
) -> ExpenseEntryRead:
    entry = await finance_service.create_expense_entry(repo, rule_repo, user.id, data)
    return ExpenseEntryRead.model_validate(entry)


@router.patch("/{entry_id}", response_model=ExpenseEntryRead)
async def update_expense(
    entry_id: uuid.UUID,
    data: ExpenseEntryUpdate,
    user: CurrentUser,
    repo: ExpenseRepository = Depends(get_expense_repository),
) -> ExpenseEntryRead:
    try:
        entry = await finance_service.update_expense_entry(repo, user.id, entry_id, data)
    except finance_service.EntryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Expense entry not found") from exc
    return ExpenseEntryRead.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    entry_id: uuid.UUID,
    user: CurrentUser,
    repo: ExpenseRepository = Depends(get_expense_repository),
) -> None:
    try:
        await finance_service.delete_expense_entry(repo, user.id, entry_id)
    except finance_service.EntryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Expense entry not found") from exc
