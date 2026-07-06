"""Password hashing: Argon2id, explicitly pinned rather than left to a library
default, so the choice is visible here rather than implicit.
"""

from __future__ import annotations

from fastapi_users.password import Argon2Hasher, PasswordHash, PasswordHelper

password_helper = PasswordHelper(PasswordHash([Argon2Hasher()]))
