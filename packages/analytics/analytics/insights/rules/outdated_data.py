"""Flags when the public reference dataset backing city/rent comparisons is
older than a reasonable freshness threshold, so users don't mistake a stale
snapshot for current data.
"""

from __future__ import annotations

from ..models import Insight, InsightContext

RULE_KEY = "outdated_data"


def evaluate(ctx: InsightContext) -> list[Insight]:
    if ctx.reference_snapshot_age_days is None:
        return []
    if ctx.reference_snapshot_age_days <= ctx.reference_snapshot_max_age_days:
        return []

    age_months = ctx.reference_snapshot_age_days // 30
    return [
        Insight(
            rule_key=RULE_KEY,
            severity="info",
            title="Referenzdaten sind veraltet",
            explanation=(
                f"Die für den Städtevergleich verwendete Referenz-Momentaufnahme ist etwa "
                f"{age_months} Monate alt. Sie wird weiterhin angezeigt, aber nicht als aktuell "
                "ausgewiesen."
            ),
            evidence={
                "reference_snapshot_age_days": ctx.reference_snapshot_age_days,
                "max_age_days": ctx.reference_snapshot_max_age_days,
            },
            confidence="high",
            suggested_action=(
                'Siehe die Seite "Datenquellen" für das genaue Datum der letzten '
                "veröffentlichten Aktualisierung."
            ),
            assumptions=(
                'Schwellenwert für "veraltet" ist ein Produktentscheid, keine externe Vorgabe.',
            ),
        )
    ]
