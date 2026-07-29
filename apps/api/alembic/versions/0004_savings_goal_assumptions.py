"""add optional illustrative return assumptions to savings goals

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-29 00:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NAMESPACE = uuid.UUID("a1f9c6c0-1c1b-4b7a-8e2a-3f6c9d2b7a10")
_SAVINGS_CATEGORY_ID = uuid.uuid5(_NAMESPACE, "category:savings")

category_table = sa.table(
    "category",
    sa.column("id", sa.UUID()),
    sa.column("user_id", sa.UUID()),
    sa.column("name", sa.String()),
    sa.column("kind", PGEnum("INCOME", "EXPENSE", name="category_kind", create_type=False)),
    sa.column("color", sa.String()),
    sa.column("icon", sa.String()),
    sa.column("is_archived", sa.Boolean()),
)


def upgrade() -> None:
    op.add_column("savings_goal", sa.Column("template_key", sa.String(length=50), nullable=True))
    op.add_column(
        "savings_goal",
        sa.Column("annual_return_min_pct", sa.Numeric(precision=5, scale=2), nullable=True),
    )
    op.add_column(
        "savings_goal",
        sa.Column("annual_return_max_pct", sa.Numeric(precision=5, scale=2), nullable=True),
    )
    op.bulk_insert(
        category_table,
        [
            {
                "id": _SAVINGS_CATEGORY_ID,
                "user_id": None,
                "name": "Sparen",
                "kind": "EXPENSE",
                "color": "#8154D8",
                "icon": "piggy-bank",
                "is_archived": False,
            }
        ],
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa.text("DELETE FROM category WHERE id = :id AND user_id IS NULL"),
        {"id": _SAVINGS_CATEGORY_ID},
    )
    op.drop_column("savings_goal", "annual_return_max_pct")
    op.drop_column("savings_goal", "annual_return_min_pct")
    op.drop_column("savings_goal", "template_key")
