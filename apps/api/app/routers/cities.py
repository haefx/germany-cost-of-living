"""City comparison, data-source freshness, and postal-code lookup."""

from __future__ import annotations

from fastapi import APIRouter

from ..deps import CurrentUser, DbSession
from ..integrations.plz_lookup import PlzLookupResult, ZippopotamAdapter, resolve_postal_code
from ..schemas.city import CityComparisonRead, DataSourceStatusRead, PlzLookupResponse
from ..services import city_service

router = APIRouter(tags=["cities"])

_plz_adapter = ZippopotamAdapter()


@router.get("/cities", response_model=list[CityComparisonRead])
async def list_city_comparisons(user: CurrentUser, session: DbSession) -> list[CityComparisonRead]:
    return await city_service.get_city_comparisons(session)


@router.get("/data-sources", response_model=list[DataSourceStatusRead])
async def list_data_sources(user: CurrentUser, session: DbSession) -> list[DataSourceStatusRead]:
    return await city_service.get_data_source_statuses(session)


@router.get("/plz/{postal_code}", response_model=PlzLookupResponse)
async def lookup_postal_code(postal_code: str, user: CurrentUser) -> PlzLookupResponse:
    result: PlzLookupResult | None = await resolve_postal_code(_plz_adapter, postal_code)
    if result is None:
        return PlzLookupResponse(found=False, postal_code=postal_code)
    return PlzLookupResponse(
        found=True, postal_code=postal_code, city=result.city, state=result.state
    )
