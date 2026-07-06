"""Income entry endpoints."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import CurrentUser, get_income_repository, get_recurrence_rule_repository
from ..repositories.finance import IncomeRepository, RecurrenceRuleRepository
from ..schemas.finance import IncomeEntryCreate, IncomeEntryRead, IncomeEntryUpdate
from ..services import finance_service

router = APIRouter(prefix="/income", tags=["income"])


@router.get("", response_model=list[IncomeEntryRead])
async def list_income(
    user: CurrentUser,
    month: date | None = None,
    repo: IncomeRepository = Depends(get_income_repository),
) -> list[IncomeEntryRead]:
    entries = await repo.list_for_month(user.id, month) if month else await repo.list(user.id)
    return [IncomeEntryRead.model_validate(entry) for entry in entries]


@router.post("", response_model=IncomeEntryRead, status_code=status.HTTP_201_CREATED)
async def create_income(
    data: IncomeEntryCreate,
    user: CurrentUser,
    repo: IncomeRepository = Depends(get_income_repository),
    rule_repo: RecurrenceRuleRepository = Depends(get_recurrence_rule_repository),
) -> IncomeEntryRead:
    entry = await finance_service.create_income_entry(repo, rule_repo, user.id, data)
    return IncomeEntryRead.model_validate(entry)


@router.patch("/{entry_id}", response_model=IncomeEntryRead)
async def update_income(
    entry_id: uuid.UUID,
    data: IncomeEntryUpdate,
    user: CurrentUser,
    repo: IncomeRepository = Depends(get_income_repository),
) -> IncomeEntryRead:
    try:
        entry = await finance_service.update_income_entry(repo, user.id, entry_id, data)
    except finance_service.EntryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Income entry not found") from exc
    return IncomeEntryRead.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    entry_id: uuid.UUID,
    user: CurrentUser,
    repo: IncomeRepository = Depends(get_income_repository),
) -> None:
    try:
        await finance_service.delete_income_entry(repo, user.id, entry_id)
    except finance_service.EntryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Income entry not found") from exc
