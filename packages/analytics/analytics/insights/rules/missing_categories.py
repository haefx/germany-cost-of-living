"""Flags a month where a material amount of spending has no category assigned,
which quietly breaks every other category-based insight and chart.
"""

from __future__ import annotations

from decimal import Decimal

from ..models import Insight, InsightContext

RULE_KEY = "missing_categories"

MIN_UNCATEGORIZED_COUNT = 3
MIN_UNCATEGORIZED_AMOUNT = Decimal("50")


def evaluate(ctx: InsightContext) -> list[Insight]:
    if (
        ctx.uncategorized_expense_count < MIN_UNCATEGORIZED_COUNT
        and ctx.uncategorized_expense_amount < MIN_UNCATEGORIZED_AMOUNT
    ):
        return []

    return [
        Insight(
            rule_key=RULE_KEY,
            severity="info",
            title="Ausgaben ohne Kategorie",
            explanation=(
                f"{ctx.uncategorized_expense_count} Ausgaben in diesem Monat "
                f"(zusammen {ctx.uncategorized_expense_amount} €) haben keine Kategorie. "
                "Ohne Kategorie können Budget- und Trendauswertungen unvollständig sein."
            ),
            evidence={
                "uncategorized_count": ctx.uncategorized_expense_count,
                "uncategorized_amount": str(ctx.uncategorized_expense_amount),
            },
            confidence="high",
            suggested_action=(
                "Ordne diesen Ausgaben eine Kategorie zu, um genauere Auswertungen zu erhalten."
            ),
            assumptions=("Zählt Ausgaben ohne zugewiesene Kategorie im aktuellen Monat.",),
        )
    ]
