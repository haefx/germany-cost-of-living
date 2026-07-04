"""seed default categories

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-05 00:00:02.000000

A data migration (not a schema change): inserts the global default
categories (``user_id IS NULL``) every account starts with. Users can archive
or add to these but the set itself is seeded once here rather than
hard-coded in application startup logic.

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NAMESPACE = uuid.UUID("a1f9c6c0-1c1b-4b7a-8e2a-3f6c9d2b7a10")


def _category_id(slug: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, f"category:{slug}")


EXPENSE_CATEGORIES = [
    ("housing", "Miete & Wohnen", "#2563EB", "home"),
    ("utilities", "Nebenkosten", "#0891B2", "droplet"),
    ("electricity", "Strom", "#EAB308", "zap"),
    ("insurance", "Versicherungen", "#7C3AED", "shield"),
    ("subscriptions", "Abos", "#DB2777", "repeat"),
    ("groceries", "Lebensmittel", "#16A34A", "shopping-cart"),
    ("mobility", "Mobilität", "#0D9488", "car"),
    ("health", "Gesundheit", "#DC2626", "heart-pulse"),
    ("children", "Kinder", "#F97316", "baby"),
    ("leisure", "Freizeit", "#9333EA", "party-popper"),
    ("communication", "Kommunikation", "#0EA5E9", "phone"),
    ("debt_financing", "Schulden & Finanzierung", "#B91C1C", "landmark"),
    ("education", "Bildung", "#4338CA", "graduation-cap"),
    ("other_expense", "Sonstiges", "#6B7280", "more-horizontal"),
]

INCOME_CATEGORIES = [
    ("salary", "Gehalt", "#16A34A", "wallet"),
    ("secondary_job", "Nebenjob", "#22C55E", "briefcase"),
    ("self_employment", "Selbstständigkeit", "#15803D", "trending-up"),
    ("benefits", "Sozialleistungen", "#65A30D", "hand-coins"),
    ("pension", "Rente", "#4D7C0F", "piggy-bank"),
    ("rental_income", "Mieteinnahmen", "#166534", "building"),
    ("other_income", "Sonstige Einnahmen", "#6B7280", "more-horizontal"),
]

category_table = sa.table(
    "category",
    sa.column("id", sa.UUID()),
    sa.column("user_id", sa.UUID()),
    sa.column("name", sa.String()),
    sa.column(
        "kind", PGEnum("INCOME", "EXPENSE", name="category_kind", create_type=False)
    ),
    sa.column("color", sa.String()),
    sa.column("icon", sa.String()),
    sa.column("is_archived", sa.Boolean()),
)


def upgrade() -> None:
    rows = [
        {
            "id": _category_id(slug),
            "user_id": None,
            "name": name,
            "kind": "EXPENSE",
            "color": color,
            "icon": icon,
            "is_archived": False,
        }
        for slug, name, color, icon in EXPENSE_CATEGORIES
    ] + [
        {
            "id": _category_id(slug),
            "user_id": None,
            "name": name,
            "kind": "INCOME",
            "color": color,
            "icon": icon,
            "is_archived": False,
        }
        for slug, name, color, icon in INCOME_CATEGORIES
    ]
    op.bulk_insert(category_table, rows)


def downgrade() -> None:
    all_slugs = [slug for slug, *_ in EXPENSE_CATEGORIES + INCOME_CATEGORIES]
    ids = [_category_id(slug) for slug in all_slugs]
    stmt = sa.text("DELETE FROM category WHERE id IN :ids AND user_id IS NULL").bindparams(
        sa.bindparam("ids", expanding=True)
    )
    op.get_bind().execute(stmt, {"ids": ids})
