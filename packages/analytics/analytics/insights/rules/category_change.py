"""Detects a category whose *share* of total monthly spending has shifted
unusually, as opposed to spending_increase which looks at the category's own
absolute amount. A category can grow in absolute terms without its share
changing (if overall spending grew too) — this rule targets the case where a
category is crowding out the rest of the budget.
"""

from __future__ import annotations

import statistics
from decimal import Decimal

from ..models import Insight, InsightContext

RULE_KEY = "unusual_category_change"

MIN_HISTORY_POINTS = 3
MIN_ABSOLUTE_SHARE_CHANGE = Decimal("0.05")  # 5 percentage points
DEVIATION_THRESHOLD_STDEV = 2.0


def evaluate(ctx: InsightContext) -> list[Insight]:
    if ctx.total_expenses <= 0:
        return []

    insights: list[Insight] = []
    history_len = len(ctx.trailing_total_expenses)

    for category in ctx.category_spending:
        historical_shares = [
            float(category.trailing_history[i] / ctx.trailing_total_expenses[i])
            for i in range(min(history_len, len(category.trailing_history)))
            if ctx.trailing_total_expenses[i] > 0
        ]
        if len(historical_shares) < MIN_HISTORY_POINTS:
            continue

        current_share = float(category.current_amount / ctx.total_expenses)
        mean_share = statistics.mean(historical_shares)
        stdev_share = statistics.pstdev(historical_shares) or 0.01
        deviation = abs(current_share - mean_share) / stdev_share
        absolute_change = Decimal(str(current_share)) - Decimal(str(mean_share))

        if (
            deviation < DEVIATION_THRESHOLD_STDEV
            or abs(absolute_change) < MIN_ABSOLUTE_SHARE_CHANGE
        ):
            continue

        direction = "gestiegen" if absolute_change > 0 else "gesunken"
        insights.append(
            Insight(
                rule_key=RULE_KEY,
                severity="info",
                title=f'Anteil von "{category.category_name}" ungewöhnlich verändert',
                explanation=(
                    f'"{category.category_name}" macht diesen Monat '
                    f"{current_share * 100:.0f}% deiner Gesamtausgaben aus, gegenüber "
                    f"durchschnittlich {mean_share * 100:.0f}% in den Vormonaten. Der Anteil "
                    f"ist ungewöhnlich {direction}, unabhängig vom absoluten Betrag."
                ),
                evidence={
                    "category_id": category.category_id,
                    "current_share": f"{current_share:.4f}",
                    "historical_mean_share": f"{mean_share:.4f}",
                    "historical_shares": [f"{s:.4f}" for s in historical_shares],
                },
                confidence="low",
                suggested_action=(
                    "Ein Blick auf die Verteilung der Ausgaben über alle Kategorien hinweg "
                    "kann zeigen, ob sich dein Ausgabenmuster insgesamt verschoben hat."
                ),
                assumptions=(
                    "Anteil bezogen auf die Gesamtausgaben des jeweiligen Monats, nicht auf "
                    "ein festes Budget.",
                ),
            )
        )
    return insights
