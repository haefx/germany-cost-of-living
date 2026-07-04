"""Schema validation (type/required-ness — a failure here excludes the row)
plus outlier bounds checks (a failure here is only a warning).
"""

from __future__ import annotations

from pydantic import ValidationError

from ..logging_setup import get_logger
from ..models import RawCityRecord, ValidationIssue
from ..outliers import check_bounds

logger = get_logger(__name__)


def run(raw_rows: list[dict[str, str]]) -> tuple[list[RawCityRecord], list[ValidationIssue]]:
    valid_records: list[RawCityRecord] = []
    issues: list[ValidationIssue] = []

    for index, raw_row in enumerate(raw_rows):
        try:
            record = RawCityRecord.model_validate(raw_row)
        except ValidationError as exc:
            city_name = raw_row.get("city") or f"row {index}"
            issues.append(
                ValidationIssue(
                    severity="error",
                    rule_key="schema_validation_failed",
                    message=f"{city_name}: {exc}",
                    city=raw_row.get("city"),
                )
            )
            logger.warning("row_rejected", row_index=index, city=raw_row.get("city"))
            continue

        valid_records.append(record)
        issues.extend(check_bounds(record))

    logger.info(
        "validate_complete",
        rows_valid=len(valid_records),
        rows_rejected=len(raw_rows) - len(valid_records),
        warnings=sum(1 for i in issues if i.severity == "warning"),
    )
    return valid_records, issues
