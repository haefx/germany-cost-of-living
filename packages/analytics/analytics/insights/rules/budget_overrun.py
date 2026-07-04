"""Detects categories where actual spending exceeds the user's own budget."""

from __future__ import annotations

from ..models import Insight, InsightContext

RULE_KEY = "budget_overrun"


def evaluate(ctx: InsightContext) -> list[Insight]:
    insights: list[Insight] = []
    for budget in ctx.budgets:
        overrun = budget.actual_spent - budget.monthly_limit
        if overrun <= 0:
            continue
        insights.append(
            Insight(
                rule_key=RULE_KEY,
                severity="warning",
                title=f'Budget "{budget.category_name}" überschritten',
                explanation=(
                    f'Für die Kategorie "{budget.category_name}" hast du ein Budget von '
                    f"{budget.monthly_limit} € pro Monat festgelegt. Die tatsächlichen "
                    f"Ausgaben liegen aktuell bei {budget.actual_spent} €."
                ),
                evidence={
                    "category_id": budget.category_id,
                    "monthly_limit": str(budget.monthly_limit),
                    "actual_spent": str(budget.actual_spent),
                },
                confidence="high",
                suggested_action=(
                    "Prüfe die Buchungen in dieser Kategorie oder passe das Budget an, "
                    "falls es nicht mehr realistisch ist."
                ),
                assumptions=("Basiert auf dem von dir selbst gesetzten Budget.",),
                estimated_savings_min=overrun,
                estimated_savings_max=overrun,
            )
        )
    return insights
