"""Budget endpoints: limits plus computed planned-vs-actual status."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import (
    CurrentUser,
    get_budget_repository,
    get_category_repository,
    get_expense_repository,
)
from ..repositories.category import CategoryRepository
from ..repositories.finance import BudgetRepository, ExpenseRepository
from ..schemas.finance import BudgetCreate, BudgetRead, BudgetStatusRead, BudgetUpdate
from ..services import finance_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetStatusRead])
async def list_budgets(
    user: CurrentUser,
    month: date | None = None,
    budget_repo: BudgetRepository = Depends(get_budget_repository),
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> list[BudgetStatusRead]:
    effective_month = month or date.today()
    return await finance_service.list_budget_statuses(
        budget_repo, expense_repo, category_repo, user.id, effective_month
    )


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreate,
    user: CurrentUser,
    repo: BudgetRepository = Depends(get_budget_repository),
) -> BudgetRead:
    budget = await finance_service.create_budget(repo, user.id, data)
    return BudgetRead.model_validate(budget)


@router.patch("/{budget_id}", response_model=BudgetRead)
async def update_budget(
    budget_id: uuid.UUID,
    data: BudgetUpdate,
    user: CurrentUser,
    repo: BudgetRepository = Depends(get_budget_repository),
) -> BudgetRead:
    try:
        budget = await finance_service.update_budget(repo, user.id, budget_id, data)
    except finance_service.BudgetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Budget not found") from exc
    return BudgetRead.model_validate(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: uuid.UUID,
    user: CurrentUser,
    repo: BudgetRepository = Depends(get_budget_repository),
) -> None:
    try:
        await finance_service.delete_budget(repo, user.id, budget_id)
    except finance_service.BudgetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Budget not found") from exc
