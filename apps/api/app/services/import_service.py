"""CSV import: preview (validate without writing) and commit (write valid,
non-duplicate rows), sharing one row-validation routine so the two never
drift apart. Column mapping is fixed rather than user-configurable in this
phase — see docs/phase-2-roadmap.md.
"""

from __future__ import annotations

import csv
import io
import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.finance import ExpenseEntry, IncomeEntry
from ..repositories.category import CategoryRepository

RowStatus = Literal["valid", "duplicate", "error"]

MAX_IMPORT_ROWS = 1000
INCOME_COLUMNS = ("label", "amount", "entry_date", "category", "notes")
EXPENSE_COLUMNS = ("label", "amount", "entry_date", "category", "merchant", "notes")


@dataclass(frozen=True)
class ImportRowResult:
    row_number: int
    status: RowStatus
    message: str
    label: str | None = None
    amount: str | None = None
    entry_date: str | None = None


@dataclass(frozen=True)
class ImportSummary:
    imported: int
    skipped_duplicates: int
    errors: list[ImportRowResult]


def _parse_csv_rows(csv_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)[:MAX_IMPORT_ROWS]


async def _resolve_category_id(
    category_repo: CategoryRepository, user_id: uuid.UUID, name: str | None
) -> uuid.UUID | None | Literal["not_found"]:
    if not name or not name.strip():
        return None
    categories = await category_repo.list_visible(user_id)
    for category in categories:
        if category.name.strip().lower() == name.strip().lower():
            return category.id
    return "not_found"


async def _validate_row(
    session: AsyncSession,
    category_repo: CategoryRepository,
    user_id: uuid.UUID,
    model: type[IncomeEntry] | type[ExpenseEntry],
    row_number: int,
    raw_row: dict[str, str],
) -> tuple[ImportRowResult, dict[str, object] | None]:
    label = (raw_row.get("label") or "").strip()
    amount_raw = (raw_row.get("amount") or "").strip()
    date_raw = (raw_row.get("entry_date") or "").strip()

    if not label:
        return ImportRowResult(row_number, "error", "label is required"), None

    try:
        amount = Decimal(amount_raw)
        if amount <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return (
            ImportRowResult(row_number, "error", f"invalid amount: {amount_raw!r}", label),
            None,
        )

    try:
        entry_date = date.fromisoformat(date_raw)
    except ValueError:
        return (
            ImportRowResult(row_number, "error", f"invalid entry_date: {date_raw!r}", label),
            None,
        )

    category_id = await _resolve_category_id(category_repo, user_id, raw_row.get("category"))
    if category_id == "not_found":
        return (
            ImportRowResult(
                row_number, "error", f"unknown category: {raw_row.get('category')!r}", label
            ),
            None,
        )

    duplicate = await session.execute(
        select(model.id).where(
            model.user_id == user_id,
            model.label == label,
            model.amount == amount,
            model.entry_date == entry_date,
        )
    )
    if duplicate.scalar_one_or_none() is not None:
        return (
            ImportRowResult(
                row_number, "duplicate", "already exists", label, str(amount), date_raw
            ),
            None,
        )

    fields: dict[str, object] = {
        "label": label,
        "amount": amount,
        "entry_date": entry_date,
        "category_id": category_id,
        "notes": (raw_row.get("notes") or "").strip() or None,
        "is_recurring": False,
    }
    if model is ExpenseEntry:
        fields["merchant"] = (raw_row.get("merchant") or "").strip() or None

    return ImportRowResult(row_number, "valid", "ok", label, str(amount), date_raw), fields


async def preview_import(
    session: AsyncSession,
    category_repo: CategoryRepository,
    user_id: uuid.UUID,
    model: type[IncomeEntry] | type[ExpenseEntry],
    csv_text: str,
) -> list[ImportRowResult]:
    results = []
    for row_number, raw_row in enumerate(_parse_csv_rows(csv_text), start=2):
        result, _ = await _validate_row(session, category_repo, user_id, model, row_number, raw_row)
        results.append(result)
    return results


async def commit_import(
    session: AsyncSession,
    category_repo: CategoryRepository,
    user_id: uuid.UUID,
    model: type[IncomeEntry] | type[ExpenseEntry],
    csv_text: str,
) -> ImportSummary:
    imported = 0
    skipped_duplicates = 0
    errors: list[ImportRowResult] = []

    for row_number, raw_row in enumerate(_parse_csv_rows(csv_text), start=2):
        result, fields = await _validate_row(
            session, category_repo, user_id, model, row_number, raw_row
        )
        if result.status == "valid" and fields is not None:
            session.add(model(user_id=user_id, **fields))
            imported += 1
        elif result.status == "duplicate":
            skipped_duplicates += 1
        else:
            errors.append(result)

    await session.flush()
    return ImportSummary(imported=imported, skipped_duplicates=skipped_duplicates, errors=errors)
