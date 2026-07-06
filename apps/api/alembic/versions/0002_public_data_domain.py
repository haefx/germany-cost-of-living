"""public data domain

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-05 00:00:01.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_source",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("license_note", sa.Text(), nullable=True),
        sa.Column("is_live_integration", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    op.create_table(
        "city",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "import_run",
        sa.Column("data_source_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "RUNNING", "SUCCESS", "PARTIAL", "FAILED", name="import_run_status"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_extracted", sa.Integer(), nullable=False),
        sa.Column("rows_loaded", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "triggered_by", sa.Enum("MANUAL", "CLI", "SCHEDULED", name="triggered_by"), nullable=False
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_source.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "salary_snapshot",
        sa.Column("city_id", sa.UUID(), nullable=False),
        sa.Column("import_run_id", sa.UUID(), nullable=False),
        sa.Column("median_gross", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["city.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "rent_snapshot",
        sa.Column("city_id", sa.UUID(), nullable=False),
        sa.Column("import_run_id", sa.UUID(), nullable=False),
        sa.Column("sqm_cold", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("avg_apartment_size", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["city.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cost_snapshot",
        sa.Column("city_id", sa.UUID(), nullable=False),
        sa.Column("import_run_id", sa.UUID(), nullable=False),
        sa.Column("groceries_month", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("transport_month", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("utilities_month", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["city.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "inflation_snapshot",
        sa.Column("city_id", sa.UUID(), nullable=True),
        sa.Column("import_run_id", sa.UUID(), nullable=False),
        sa.Column("rate_pct", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["city.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "validation_result",
        sa.Column("import_run_id", sa.UUID(), nullable=False),
        sa.Column("city_id", sa.UUID(), nullable=True),
        sa.Column(
            "severity", sa.Enum("INFO", "WARNING", "ERROR", name="validation_severity"), nullable=False
        ),
        sa.Column("rule_key", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("field", sa.String(length=100), nullable=True),
        sa.Column("observed_value", sa.String(length=200), nullable=True),
        sa.Column("expected_range", sa.String(length=200), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["city.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("validation_result")
    op.drop_table("inflation_snapshot")
    op.drop_table("cost_snapshot")
    op.drop_table("rent_snapshot")
    op.drop_table("salary_snapshot")
    op.drop_table("import_run")
    op.drop_table("city")
    op.drop_table("data_source")
    sa.Enum(name="validation_severity").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="triggered_by").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="import_run_status").drop(op.get_bind(), checkfirst=True)
