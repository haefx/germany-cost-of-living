"""Ownership-enforced repository base.

Every table that belongs to a user has a ``user_id`` column. Every query
here filters on it. ``user_id`` is a required argument on every method — a
caller cannot construct a ``get``/``update``/`delete`` without supplying it,
and it must come from the authenticated request (``current_active_user``),
never from a path or query parameter. This is what makes cross-user access
structurally impossible to forget to check, rather than a convention that
has to be remembered in every router.

Accessing another user's row through any of these methods behaves exactly
like the row not existing (``None`` / zero rows affected) — the API layer
turns that into a 404, not a 403, so a caller cannot distinguish "not yours"
from "does not exist" and enumerate other users' resource ids.
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol, cast

from sqlalchemy import CursorResult, select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped


class _UserOwnedModel(Protocol):
    id: Mapped[uuid.UUID]
    # Typed loosely (some owned models allow a NULL user_id for global rows,
    # e.g. Category) — Protocol attribute matching is invariant, so a precise
    # `Mapped[uuid.UUID | None]` here would reject the non-nullable owners.
    user_id: Mapped[Any]


class UserOwnedRepository[ModelT: _UserOwnedModel]:
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, user_id: uuid.UUID) -> list[ModelT]:
        result = await self.session.execute(select(self.model).where(self.model.user_id == user_id))
        return list(result.scalars().all())

    async def get(self, user_id: uuid.UUID, entity_id: uuid.UUID) -> ModelT | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id, self.model.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: uuid.UUID, **fields: Any) -> ModelT:
        # `model` is bound to the structural `_UserOwnedModel` protocol, which
        # has no constructor signature of its own for mypy to check against.
        entity = self.model(user_id=user_id, **fields)  # type: ignore[call-arg]
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(
        self, user_id: uuid.UUID, entity_id: uuid.UUID, **fields: Any
    ) -> ModelT | None:
        entity = await self.get(user_id, entity_id)
        if entity is None:
            return None
        for key, value in fields.items():
            setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, user_id: uuid.UUID, entity_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            sa_delete(self.model).where(self.model.id == entity_id, self.model.user_id == user_id)
        )
        return cast(CursorResult[Any], result).rowcount > 0
