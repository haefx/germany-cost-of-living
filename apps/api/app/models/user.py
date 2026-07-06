"""User accounts and revocable sessions (fastapi-users tables).

``User`` extends fastapi-users' base user table with the two columns this
application needs for demo accounts. Demo users still get a real (but
synthetic, non-guessable) email and password hash, because fastapi-users'
base table enforces NOT NULL + UNIQUE on both — a demo user never actually
authenticates with them, since its session is issued directly by the demo
endpoint rather than through the password-login flow.

``AccessToken`` backs a database-persisted session strategy: logging out
deletes the row, which immediately and genuinely revokes that session,
unlike a stateless JWT that would need a separate denylist to revoke early.
"""

from __future__ import annotations

from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "user"

    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    demo_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccessToken(Base, SQLAlchemyBaseAccessTokenTableUUID):
    __tablename__ = "accesstoken"
