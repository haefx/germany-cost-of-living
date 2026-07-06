"""Session transport and strategy: an HttpOnly, SameSite cookie backed by a
database-persisted access token. Chosen over a stateless JWT specifically so
that logout is a real revocation (the token row is deleted) rather than a
client-side-only action — a stolen or leaked cookie can be invalidated
server-side.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy import DatabaseStrategy
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from ..config import get_settings
from ..db import get_session
from ..models.user import AccessToken

settings = get_settings()

SESSION_LIFETIME_SECONDS = 60 * 60 * 24 * 30  # 30 days

cookie_transport = CookieTransport(
    cookie_name="gcol_session",
    cookie_max_age=SESSION_LIFETIME_SECONDS,
    cookie_secure=settings.cookie_secure,
    cookie_httponly=True,
    cookie_samesite="lax",
    cookie_domain=settings.cookie_domain or None,
)


async def get_access_token_db(
    session=Depends(get_session),
) -> AsyncGenerator[SQLAlchemyAccessTokenDatabase, None]:
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


def get_database_strategy(
    access_token_db: SQLAlchemyAccessTokenDatabase = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=SESSION_LIFETIME_SECONDS)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
