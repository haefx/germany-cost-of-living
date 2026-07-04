"""Category service: the only layer routers talk to for category operations."""

from __future__ import annotations

import uuid

from ..models.finance import Category
from ..repositories.category import CategoryRepository
from ..schemas.finance import CategoryCreate, CategoryUpdate


class CategoryNotFoundError(Exception):
    pass


async def list_categories(repo: CategoryRepository, user_id: uuid.UUID) -> list[Category]:
    return await repo.list_visible(user_id)


async def create_category(
    repo: CategoryRepository, user_id: uuid.UUID, data: CategoryCreate
) -> Category:
    return await repo.create(user_id, **data.model_dump())


async def update_category(
    repo: CategoryRepository, user_id: uuid.UUID, category_id: uuid.UUID, data: CategoryUpdate
) -> Category:
    updated = await repo.update(
        user_id, category_id, **data.model_dump(exclude_unset=True)
    )
    if updated is None:
        raise CategoryNotFoundError
    return updated


async def delete_category(
    repo: CategoryRepository, user_id: uuid.UUID, category_id: uuid.UUID
) -> None:
    deleted = await repo.delete(user_id, category_id)
    if not deleted:
        raise CategoryNotFoundError
