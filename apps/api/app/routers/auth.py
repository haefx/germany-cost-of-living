"""Authentication routes: register, cookie login/logout, password reset,
and the current-user profile endpoint. All provided by fastapi-users; this
module just assembles them under one router.
"""

from __future__ import annotations

from fastapi import APIRouter

from ..schemas.auth import UserCreate, UserRead, UserUpdate
from ..security.backend import auth_backend
from ..security.users import fastapi_users

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"])
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)
