"""Savings goal endpoints, including nested contributions."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import (
    CurrentUser,
    get_expense_repository,
    get_savings_goal_contribution_repository,
    get_savings_goal_repository,
)
from ..repositories.finance import (
    ExpenseRepository,
    SavingsGoalContributionRepository,
    SavingsGoalRepository,
)
from ..schemas.finance import (
    SavingsGoalContributionCreate,
    SavingsGoalContributionRead,
    SavingsGoalCreate,
    SavingsGoalProgressRead,
    SavingsGoalRead,
    SavingsGoalUpdate,
)
from ..services import finance_service

router = APIRouter(prefix="/savings-goals", tags=["savings-goals"])


@router.get("", response_model=list[SavingsGoalProgressRead])
async def list_savings_goals(
    user: CurrentUser,
    goal_repo: SavingsGoalRepository = Depends(get_savings_goal_repository),
    contribution_repo: SavingsGoalContributionRepository = Depends(
        get_savings_goal_contribution_repository
    ),
) -> list[SavingsGoalProgressRead]:
    goals = await goal_repo.list(user.id)
    return [await finance_service.goal_progress(contribution_repo, goal) for goal in goals]


@router.post("", response_model=SavingsGoalRead, status_code=status.HTTP_201_CREATED)
async def create_savings_goal(
    data: SavingsGoalCreate,
    user: CurrentUser,
    repo: SavingsGoalRepository = Depends(get_savings_goal_repository),
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
) -> SavingsGoalRead:
    try:
        goal = await finance_service.create_savings_goal(repo, expense_repo, user.id, data)
    except finance_service.LinkedExpenseNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Linked expense not found") from exc
    return SavingsGoalRead.model_validate(goal)


@router.patch("/{goal_id}", response_model=SavingsGoalRead)
async def update_savings_goal(
    goal_id: uuid.UUID,
    data: SavingsGoalUpdate,
    user: CurrentUser,
    repo: SavingsGoalRepository = Depends(get_savings_goal_repository),
) -> SavingsGoalRead:
    try:
        goal = await finance_service.update_savings_goal(repo, user.id, goal_id, data)
    except finance_service.SavingsGoalNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Savings goal not found") from exc
    return SavingsGoalRead.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_savings_goal(
    goal_id: uuid.UUID,
    user: CurrentUser,
    repo: SavingsGoalRepository = Depends(get_savings_goal_repository),
) -> None:
    try:
        await finance_service.delete_savings_goal(repo, user.id, goal_id)
    except finance_service.SavingsGoalNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Savings goal not found") from exc


@router.post(
    "/{goal_id}/contributions",
    response_model=SavingsGoalContributionRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_contribution(
    goal_id: uuid.UUID,
    data: SavingsGoalContributionCreate,
    user: CurrentUser,
    repo: SavingsGoalContributionRepository = Depends(get_savings_goal_contribution_repository),
) -> SavingsGoalContributionRead:
    try:
        contribution = await finance_service.add_contribution(repo, user.id, goal_id, data)
    except finance_service.SavingsGoalNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Savings goal not found") from exc
    return SavingsGoalContributionRead.model_validate(contribution)


@router.delete("/{goal_id}/contributions/{contribution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contribution(
    goal_id: uuid.UUID,
    contribution_id: uuid.UUID,
    user: CurrentUser,
    repo: SavingsGoalContributionRepository = Depends(get_savings_goal_contribution_repository),
) -> None:
    try:
        await finance_service.delete_contribution(repo, user.id, goal_id, contribution_id)
    except finance_service.ContributionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contribution not found") from exc
