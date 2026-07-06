from __future__ import annotations

from ..adapters.base import SourceAdapter
from ..logging_setup import get_logger

logger = get_logger(__name__)


def run(adapter: SourceAdapter) -> list[dict[str, str]]:
    rows = adapter.extract()
    logger.info("extract_complete", rows_extracted=len(rows))
    return rows
