"""Self-service account actions not covered by fastapi-users' own router
(which only exposes admin-gated delete-by-id, not delete-your-own-account).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ..deps import CurrentUser
from ..security.manager import UserManager, get_user_manager

router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_account(
    user: CurrentUser,
    user_manager: UserManager = Depends(get_user_manager),
) -> None:
    await user_manager.delete(user)
