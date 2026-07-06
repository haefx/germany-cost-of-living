"""Category endpoints: global defaults plus the current user's own custom
categories. Only a user's own custom categories can be modified or deleted.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import CurrentUser, get_category_repository
from ..repositories.category import CategoryRepository
from ..schemas.finance import CategoryCreate, CategoryRead, CategoryUpdate
from ..services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    user: CurrentUser, repo: CategoryRepository = Depends(get_category_repository)
) -> list[CategoryRead]:
    categories = await category_service.list_categories(repo, user.id)
    return [CategoryRead.model_validate(category) for category in categories]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    user: CurrentUser,
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryRead:
    category = await category_service.create_category(repo, user.id, data)
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    user: CurrentUser,
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryRead:
    try:
        category = await category_service.update_category(repo, user.id, category_id, data)
    except category_service.CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found") from exc
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    user: CurrentUser,
    repo: CategoryRepository = Depends(get_category_repository),
) -> None:
    try:
        await category_service.delete_category(repo, user.id, category_id)
    except category_service.CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found") from exc
