"""FastAPI application factory: middleware, routers, and lifespan hooks."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import account, auth, budgets, categories, data, demo, expenses, income, savings_goals
from .scheduler import start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Germany Cost of Living API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# account.router's DELETE /users/me must be registered before auth.router's
# fastapi-users sub-router, whose DELETE /users/{id} would otherwise match
# "me" as a literal {id} value first (Starlette matches routes in
# registration order, not by specificity) and reject it as non-superuser
# before our own route ever gets a chance. See test_account_deletion.py.
app.include_router(account.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(income.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(savings_goals.router, prefix="/api")
app.include_router(data.router, prefix="/api")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
