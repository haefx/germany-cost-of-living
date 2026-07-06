"""Composition root for fastapi-users: wires the user manager and auth
backend together and exposes the dependencies routers use to require an
authenticated user.
"""

from __future__ import annotations

import uuid

from fastapi_users import FastAPIUsers

from ..models.user import User
from .backend import auth_backend
from .manager import get_user_manager

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
