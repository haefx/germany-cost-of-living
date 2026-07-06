"""Demo-household expiry, run as a job inside the API process itself.

Deliberately not a separate worker service: the job is a single cheap query
running once an hour, which does not justify the operational cost of a
second container, a message queue, or Redis.
"""

from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .db import async_session_factory
from .services.demo_service import expire_demo_users

logger = structlog.get_logger(__name__)

scheduler = AsyncIOScheduler()


async def _expire_demo_users_job() -> None:
    async with async_session_factory() as session:
        try:
            count = await expire_demo_users(session)
            await session.commit()
            if count:
                logger.info("demo_users_expired", count=count)
        except Exception:
            await session.rollback()
            logger.exception("demo_expiry_job_failed")
            raise


def start_scheduler() -> None:
    scheduler.add_job(
        _expire_demo_users_job,
        trigger="interval",
        hours=1,
        id="expire_demo_users",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
