"""Category repository.

Categories are the one entity with rows that are not user-owned: global
default categories have ``user_id IS NULL`` and are visible to everyone.
``list_visible`` is a category-specific query on top of the ownership-scoped
base; the inherited ``get``/``update``/``delete`` still only ever operate on
a user's own custom categories, so nobody can edit or delete a global default
through this repository.
"""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select

from ..models.finance import Category
from .base import UserOwnedRepository


class CategoryRepository(UserOwnedRepository[Category]):
    model = Category

    async def list_visible(self, user_id: uuid.UUID) -> list[Category]:
        result = await self.session.execute(
            select(Category)
            .where(or_(Category.user_id == user_id, Category.user_id.is_(None)))
            .where(Category.is_archived.is_(False))
            .order_by(Category.kind, Category.name)
        )
        return list(result.scalars().all())
