"""User manager: the fastapi-users hook point for registration and password
reset. No transactional email provider exists in this phase, so the reset
token is logged server-side rather than emailed — a real limitation, tracked
in docs/phase-2-roadmap.md, not hidden.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import structlog
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from ..config import get_settings
from ..db import get_session
from ..models.user import User
from .password import password_helper

logger = structlog.get_logger(__name__)
settings = get_settings()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.session_secret
    verification_token_secret = settings.session_secret

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ) -> None:
        logger.info("password_reset_requested", user_id=str(user.id))


async def get_user_db(
    session=Depends(get_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db, password_helper)
