"""Flags a month where total expenses exceed total income."""

from __future__ import annotations

from ..models import Insight, InsightContext

RULE_KEY = "negative_cash_flow"


def evaluate(ctx: InsightContext) -> list[Insight]:
    shortfall = ctx.total_expenses - ctx.total_income
    if shortfall <= 0:
        return []

    return [
        Insight(
            rule_key=RULE_KEY,
            severity="critical",
            title="Ausgaben übersteigen Einnahmen",
            explanation=(
                f"Diesen Monat stehen {ctx.total_expenses} € Ausgaben nur "
                f"{ctx.total_income} € Einnahmen gegenüber — ein Minus von {shortfall} €."
            ),
            evidence={
                "total_income": str(ctx.total_income),
                "total_expenses": str(ctx.total_expenses),
                "shortfall": str(shortfall),
            },
            confidence="high",
            suggested_action=(
                "Prüfe, ob es sich um eine einmalige Ausnahme handelt oder ob laufende "
                "Ausgaben dauerhaft über den Einnahmen liegen."
            ),
            assumptions=("Basiert auf allen für diesen Monat erfassten Einnahmen und Ausgaben.",),
            estimated_savings_min=None,
            estimated_savings_max=None,
        )
    ]
