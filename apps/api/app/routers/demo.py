"""Anonymous demo-household provisioning."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi_users.authentication.strategy import DatabaseStrategy
from starlette.responses import Response

from ..deps import DbSession
from ..security.backend import auth_backend, get_database_strategy
from ..services import demo_service

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/start")
async def start_demo(
    session: DbSession,
    strategy: DatabaseStrategy = Depends(get_database_strategy),
) -> Response:
    user = await demo_service.provision_demo_user(session)
    return await auth_backend.login(strategy, user)
