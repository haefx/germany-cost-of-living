"""Normalizes city/state name strings (unicode form, whitespace) so the
same city from different source snapshots always matches on name."""

from __future__ import annotations

import unicodedata

from ..models import RawCityRecord


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()


def run(records: list[RawCityRecord]) -> list[RawCityRecord]:
    return [
        record.model_copy(
            update={
                "city": _normalize_text(record.city),
                "state": _normalize_text(record.state),
            }
        )
        for record in records
    ]
