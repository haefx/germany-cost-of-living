"""Detects a category whose current-month total is materially above its own
trailing average — distinct from unusual_category_change, which looks at a
category's *share* of total spending rather than its absolute amount.
"""

from __future__ import annotations

from decimal import Decimal

from ..models import Insight, InsightContext

RULE_KEY = "spending_increase"

RELATIVE_THRESHOLD = Decimal("0.25")  # 25% above trailing average
ABSOLUTE_THRESHOLD = Decimal("20")  # and at least 20 EUR, to ignore noise on small categories


def evaluate(ctx: InsightContext) -> list[Insight]:
    insights: list[Insight] = []
    for category in ctx.category_spending:
        if category.trailing_average <= 0:
            continue
        increase = category.current_amount - category.trailing_average
        relative_increase = increase / category.trailing_average
        if increase < ABSOLUTE_THRESHOLD or relative_increase < RELATIVE_THRESHOLD:
            continue
        insights.append(
            Insight(
                rule_key=RULE_KEY,
                severity="info",
                title=f'Ausgaben in "{category.category_name}" gestiegen',
                explanation=(
                    f'Die Ausgaben in "{category.category_name}" liegen diesen Monat bei '
                    f"{category.current_amount} € und damit "
                    f"{relative_increase * 100:.0f}% über dem Durchschnitt der "
                    f"vorherigen Monate ({category.trailing_average} €)."
                ),
                evidence={
                    "category_id": category.category_id,
                    "current_amount": str(category.current_amount),
                    "trailing_average": str(category.trailing_average),
                    "trailing_history": [str(v) for v in category.trailing_history],
                },
                confidence="medium",
                suggested_action=(
                    "Ein Vergleich der einzelnen Buchungen in dieser Kategorie kann sich lohnen, "
                    "um die Ursache des Anstiegs zu verstehen."
                ),
                assumptions=(
                    "Vergleich basiert auf dem gleitenden Durchschnitt der letzten erfassten "
                    "Monate.",
                ),
                estimated_savings_min=Decimal("0"),
                estimated_savings_max=increase,
            )
        )
    return insights
