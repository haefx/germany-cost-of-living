"""Public reference-data schema: sources, import runs, and versioned
snapshots. Every publicly displayed figure traces back to exactly one
``ImportRun``, which records where it came from and when.

The app only ever reads the latest *published* run per data source
(``ImportRun.published_at is not None``, ordered by ``published_at desc``) —
never a bare ``MAX(year)`` aggregate. This is a deliberate fix for a bug in
the original prototype, where different queries hardcoded different years
(2023 vs. 2024) and could silently mix snapshots.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ImportRunStatus(enum.StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class TriggeredBy(enum.StrEnum):
    MANUAL = "manual"
    CLI = "cli"
    SCHEDULED = "scheduled"


class ValidationSeverity(enum.StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DataSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "data_source"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_live_integration: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ImportRun(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "import_run"

    data_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_source.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ImportRunStatus] = mapped_column(
        Enum(ImportRunStatus, name="import_run_status"),
        default=ImportRunStatus.PENDING,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rows_extracted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[TriggeredBy] = mapped_column(
        Enum(TriggeredBy, name="triggered_by"), default=TriggeredBy.MANUAL, nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SalarySnapshot(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "salary_snapshot"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=False
    )
    import_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_run.id", ondelete="CASCADE"), nullable=False
    )
    median_gross: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)


class RentSnapshot(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "rent_snapshot"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=False
    )
    import_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_run.id", ondelete="CASCADE"), nullable=False
    )
    sqm_cold: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    avg_apartment_size: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)


class CostSnapshot(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "cost_snapshot"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=False
    )
    import_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_run.id", ondelete="CASCADE"), nullable=False
    )
    groceries_month: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    transport_month: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    utilities_month: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)


class InflationSnapshot(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "inflation_snapshot"

    city_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=True
    )
    import_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_run.id", ondelete="CASCADE"), nullable=False
    )
    rate_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)


class ValidationResult(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "validation_result"

    import_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_run.id", ondelete="CASCADE"), nullable=False
    )
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id", ondelete="CASCADE"), nullable=True
    )
    severity: Mapped[ValidationSeverity] = mapped_column(
        Enum(ValidationSeverity, name="validation_severity"), nullable=False
    )
    rule_key: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observed_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    expected_range: Mapped[str | None] = mapped_column(String(200), nullable=True)
