"""Onboarding nudge: without a net income figure, categories, or budgets, no
other insight rule can produce meaningful output. This rule fires instead of
letting the dashboard silently show nothing.
"""

from __future__ import annotations

from ..models import Insight, InsightContext

RULE_KEY = "missing_inputs"


def evaluate(ctx: InsightContext) -> list[Insight]:
    missing: list[str] = []
    if ctx.net_income is None:
        missing.append("Nettoeinkommen")
    if not ctx.has_any_categories:
        missing.append("Kategorien")
    if not ctx.has_any_budgets:
        missing.append("Budgets")

    if not missing:
        return []

    return [
        Insight(
            rule_key=RULE_KEY,
            severity="info",
            title="Einige Angaben fehlen noch",
            explanation=(
                "Folgende Angaben fehlen noch, um genauere Auswertungen zu ermöglichen: "
                + ", ".join(missing)
                + "."
            ),
            evidence={"missing_inputs": missing},
            confidence="high",
            suggested_action="Ergänze die fehlenden Angaben in den Einstellungen bzw. bei Budgets.",
            assumptions=(),
        )
    ]
