"""Shared FastAPI dependencies: the current user and repository factories."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .models.user import User
from .repositories.category import CategoryRepository
from .security.users import current_active_user

CurrentUser = Annotated[User, Depends(current_active_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]


def get_category_repository(session: DbSession) -> CategoryRepository:
    return CategoryRepository(session)
