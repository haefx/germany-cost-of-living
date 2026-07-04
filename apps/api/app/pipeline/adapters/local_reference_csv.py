"""Reads the checked-in reference dataset (see data/reference/ and
docs/data-provenance.md for what it is and, just as importantly, what it
is not: a live-fetched, license-verified government dataset).

Retry/backoff is applied even though the source is a local file, because
the adapter boundary is meant to be swappable for a real HTTP source later
without changing anything downstream — the retry behavior should already
be in place when that swap happens, not bolted on afterward.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class SourceReadError(Exception):
    pass


class LocalReferenceCsvAdapter:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path

    @retry(
        retry=retry_if_exception_type(SourceReadError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    def extract(self) -> list[dict[str, str]]:
        try:
            with self.csv_path.open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))
        except OSError as exc:
            raise SourceReadError(f"Could not read {self.csv_path}: {exc}") from exc
