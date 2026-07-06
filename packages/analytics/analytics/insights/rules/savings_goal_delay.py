"""Detects savings goals that are on track to miss their target date, based
on the actual trailing contribution rate versus the rate that would be
required to hit the goal on time.
"""

from __future__ import annotations

import math
from decimal import Decimal

from ..models import Insight, InsightContext

RULE_KEY = "savings_goal_delay"

TOLERANCE = Decimal("0.10")  # 10% shortfall tolerance before flagging


def _months_between(
    earlier_year: int, earlier_month: int, later_year: int, later_month: int
) -> int:
    return (later_year - earlier_year) * 12 + (later_month - earlier_month)


def evaluate(ctx: InsightContext) -> list[Insight]:
    insights: list[Insight] = []
    for goal in ctx.savings_goals:
        remaining_amount = goal.target_amount - goal.current_amount
        if remaining_amount <= 0 or goal.target_date is None:
            continue

        months_remaining = _months_between(
            ctx.month.year, ctx.month.month, goal.target_date.year, goal.target_date.month
        )

        if months_remaining <= 0:
            insights.append(_overdue_insight(goal, remaining_amount))
            continue

        required_monthly_rate = remaining_amount / months_remaining
        shortfall = required_monthly_rate - goal.trailing_monthly_contribution_avg
        if shortfall <= required_monthly_rate * TOLERANCE:
            continue

        if goal.trailing_monthly_contribution_avg > 0:
            months_needed = math.ceil(remaining_amount / goal.trailing_monthly_contribution_avg)
            delay_months = months_needed - months_remaining
            explanation = (
                f"Beim aktuellen Sparverhalten ({goal.trailing_monthly_contribution_avg} €/Monat) "
                f'wird das Ziel "{goal.name}" voraussichtlich erst in {months_needed} statt in '
                f"{months_remaining} Monaten erreicht — etwa {delay_months} Monate später "
                "als geplant."
            )
        else:
            explanation = (
                f'Für das Ziel "{goal.name}" wurden in den letzten Monaten keine Beiträge '
                f"erfasst. Bei {months_remaining} verbleibenden Monaten wären "
                f"{required_monthly_rate} €/Monat nötig."
            )

        insights.append(
            Insight(
                rule_key=RULE_KEY,
                severity="warning",
                title=f'Sparziel "{goal.name}" im Verzug',
                explanation=explanation,
                evidence={
                    "goal_id": goal.id,
                    "remaining_amount": str(remaining_amount),
                    "months_remaining": months_remaining,
                    "required_monthly_rate": str(required_monthly_rate),
                    "trailing_monthly_contribution_avg": str(
                        goal.trailing_monthly_contribution_avg
                    ),
                },
                confidence="medium",
                suggested_action=(
                    "Erhöhe den monatlichen Beitrag oder passe das Zieldatum an, falls es "
                    "realistischer eingeschätzt werden soll."
                ),
                assumptions=(
                    "Projektion basiert auf dem gleitenden Durchschnitt der letzten erfassten "
                    "Beiträge, nicht auf einer verbindlichen Zusage.",
                ),
                estimated_savings_min=None,
                estimated_savings_max=None,
            )
        )
    return insights


def _overdue_insight(goal, remaining_amount: Decimal) -> Insight:
    return Insight(
        rule_key=RULE_KEY,
        severity="critical",
        title=f'Sparziel "{goal.name}" überfällig',
        explanation=(
            f'Das Zieldatum für "{goal.name}" liegt in der Vergangenheit oder im aktuellen '
            f"Monat, aber es fehlen noch {remaining_amount} € zum Ziel."
        ),
        evidence={"goal_id": goal.id, "remaining_amount": str(remaining_amount)},
        confidence="high",
        suggested_action="Aktualisiere das Zieldatum oder erhöhe kurzfristig den Beitrag.",
        assumptions=("Bezieht sich auf das von dir gesetzte Zieldatum.",),
    )
