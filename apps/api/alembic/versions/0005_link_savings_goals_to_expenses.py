"""link savings goals to recurring expense entries

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-29 00:00:01.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "savings_goal",
        sa.Column("monthly_contribution", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "savings_goal", sa.Column("contribution_start_date", sa.Date(), nullable=True)
    )
    op.add_column("savings_goal", sa.Column("linked_expense_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_savings_goal_linked_expense",
        "savings_goal",
        "expense_entry",
        ["linked_expense_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_savings_goal_linked_expense", "savings_goal", type_="foreignkey")
    op.drop_column("savings_goal", "linked_expense_id")
    op.drop_column("savings_goal", "contribution_start_date")
    op.drop_column("savings_goal", "monthly_contribution")
