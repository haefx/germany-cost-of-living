"""Force-expire and delete every demo account immediately, regardless of its
TTL. Intended for operators who want a clean slate right before showing the
app live, without waiting for the hourly scheduler.

Usage: ``python scripts/demo_reset.py`` (run from ``apps/api``).
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import update

from app.db import async_session_factory
from app.models.user import User
from app.services.demo_service import expire_demo_users


async def main() -> None:
    async with async_session_factory() as session:
        # Back-date every demo user's TTL so the shared expiry logic deletes
        # all of them right now, rather than duplicating the delete query here.
        await session.execute(
            update(User).where(User.is_demo.is_(True)).values(demo_expires_at=datetime.now(UTC))
        )
        count = await expire_demo_users(session)
        await session.commit()
        print(f"Deleted {count} demo account(s).")


if __name__ == "__main__":
    asyncio.run(main())
