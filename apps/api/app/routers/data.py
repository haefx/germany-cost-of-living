"""CSV import/export and full-account JSON export."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from ..deps import (
    CurrentUser,
    DbSession,
    get_category_repository,
    get_expense_repository,
    get_income_repository,
)
from ..models.finance import ExpenseEntry, IncomeEntry
from ..repositories.category import CategoryRepository
from ..repositories.finance import ExpenseRepository, IncomeRepository
from ..services import export_service, import_service

router = APIRouter(tags=["data"])

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB is generous for a personal CSV import


async def _read_csv_upload(file: UploadFile) -> str:
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Please upload a .csv file")
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Please upload a .csv file")
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File is too large")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File must be UTF-8 encoded") from exc


def _model_for(entity: Literal["income", "expenses"]) -> type[IncomeEntry] | type[ExpenseEntry]:
    return IncomeEntry if entity == "income" else ExpenseEntry


@router.post("/import/{entity}/preview")
async def preview_csv_import(
    entity: Literal["income", "expenses"],
    user: CurrentUser,
    session: DbSession,
    category_repo: CategoryRepository = Depends(get_category_repository),
    file: UploadFile = File(...),
) -> list[dict[str, Any]]:
    csv_text = await _read_csv_upload(file)
    results = await import_service.preview_import(
        session, category_repo, user.id, _model_for(entity), csv_text
    )
    return [result.__dict__ for result in results]


@router.post("/import/{entity}/commit")
async def commit_csv_import(
    entity: Literal["income", "expenses"],
    user: CurrentUser,
    session: DbSession,
    category_repo: CategoryRepository = Depends(get_category_repository),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    csv_text = await _read_csv_upload(file)
    summary = await import_service.commit_import(
        session, category_repo, user.id, _model_for(entity), csv_text
    )
    return {
        "imported": summary.imported,
        "skipped_duplicates": summary.skipped_duplicates,
        "errors": [error.__dict__ for error in summary.errors],
    }


@router.get("/export/{entity}.csv")
async def export_csv(
    entity: Literal["income", "expenses"],
    user: CurrentUser,
    category_repo: CategoryRepository = Depends(get_category_repository),
    income_repo: IncomeRepository = Depends(get_income_repository),
    expense_repo: ExpenseRepository = Depends(get_expense_repository),
) -> Response:
    categories = await category_repo.list_visible(user.id)
    category_names: export_service.CategoryNames = {
        category.id: category.name for category in categories
    }

    if entity == "income":
        income_entries = await income_repo.list(user.id)
        csv_text = export_service.income_entries_to_csv(income_entries, category_names)
    else:
        expense_entries = await expense_repo.list(user.id)
        csv_text = export_service.expense_entries_to_csv(expense_entries, category_names)

    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{entity}.csv"'},
    )


@router.get("/export/account")
async def export_account(user: CurrentUser, session: DbSession) -> dict[str, Any]:
    return await export_service.export_account_data(session, user)
