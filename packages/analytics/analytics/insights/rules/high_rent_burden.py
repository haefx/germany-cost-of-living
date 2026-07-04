"""Flags a rent burden above the common 30%/40% rules-of-thumb reference bands."""

from __future__ import annotations

from ...rent_burden import CRITICAL_THRESHOLD_PCT, WARNING_THRESHOLD_PCT, rent_burden_pct
from ..models import Insight, InsightContext, Severity

RULE_KEY = "high_rent_burden"


def evaluate(ctx: InsightContext) -> list[Insight]:
    if ctx.rent_amount is None or ctx.net_income is None or ctx.net_income <= 0:
        return []

    pct = rent_burden_pct(ctx.rent_amount, ctx.net_income)
    if pct < WARNING_THRESHOLD_PCT:
        return []

    severity: Severity = "critical" if pct >= CRITICAL_THRESHOLD_PCT else "warning"
    return [
        Insight(
            rule_key=RULE_KEY,
            severity=severity,
            title="Hohe Mietbelastung",
            explanation=(
                f"Deine Miete beträgt {pct}% deines Nettoeinkommens. Als grobe Orientierung "
                f"gilt ein Anteil über {WARNING_THRESHOLD_PCT}% als angespannt und über "
                f"{CRITICAL_THRESHOLD_PCT}% als deutlich erhöht."
            ),
            evidence={
                "rent_amount": str(ctx.rent_amount),
                "net_income": str(ctx.net_income),
                "rent_burden_pct": str(pct),
            },
            confidence="high",
            suggested_action=(
                "Ein Vergleich mit den Referenzwerten anderer Städte kann einordnen, ob dies "
                "regional üblich ist (siehe Städtevergleich)."
            ),
            assumptions=(
                "30%/40% sind gebräuchliche Orientierungswerte aus der wohnungspolitischen "
                "Diskussion, keine gesetzliche Schwelle.",
            ),
        )
    ]
