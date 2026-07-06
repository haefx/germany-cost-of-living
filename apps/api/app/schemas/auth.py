"""User account schemas. ``is_demo``/``demo_expires_at`` are read-only —
neither is accepted from client input, since a client setting them itself
would defeat the point of a demo account.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    is_demo: bool
    demo_expires_at: datetime | None


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
