"""Postal-code lookup via api.zippopotam.us — a real, free, no-key public
API (not scraping). ``resolve_postal_code`` never raises: a network failure
or unexpected response degrades to "unavailable" so the caller can fall
back to manual city selection rather than showing an error page.

A bundled offline PLZ dataset would be a natural second adapter to try
before giving up entirely; none is bundled yet (see docs/phase-2-roadmap.md).
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

logger = structlog.get_logger(__name__)

ZIPPOPOTAM_BASE_URL = "https://api.zippopotam.us/de"


@dataclass(frozen=True)
class PlzLookupResult:
    postal_code: str
    city: str
    state: str


class ZippopotamAdapter:
    def __init__(self, timeout: float = 5.0) -> None:
        self.timeout = timeout

    async def lookup(self, postal_code: str) -> PlzLookupResult:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{ZIPPOPOTAM_BASE_URL}/{postal_code}")
            response.raise_for_status()
            data = response.json()
            place = data["places"][0]
            return PlzLookupResult(
                postal_code=postal_code, city=place["place name"], state=place["state"]
            )


async def resolve_postal_code(
    adapter: ZippopotamAdapter, postal_code: str
) -> PlzLookupResult | None:
    try:
        return await adapter.lookup(postal_code)
    except Exception as exc:
        logger.warning("plz_lookup_unavailable", postal_code=postal_code, error=str(exc))
        return None
