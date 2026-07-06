import dataclasses
from decimal import Decimal

from analytics.insights.models import BudgetStatus
from analytics.insights.rules import budget_overrun


def test_fires_when_spending_exceeds_budget(base_context):
    ctx = dataclasses.replace(
        base_context,
        budgets=(
            BudgetStatus(
                category_id="cat-1",
                category_name="Lebensmittel",
                monthly_limit=Decimal("300"),
                actual_spent=Decimal("350"),
            ),
        ),
    )
    insights = budget_overrun.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].estimated_savings_max == Decimal("50")


def test_does_not_fire_at_exactly_the_limit(base_context):
    ctx = dataclasses.replace(
        base_context,
        budgets=(
            BudgetStatus(
                category_id="cat-1",
                category_name="Lebensmittel",
                monthly_limit=Decimal("300"),
                actual_spent=Decimal("300"),
            ),
        ),
    )
    assert budget_overrun.evaluate(ctx) == []


def test_does_not_fire_when_under_budget(base_context):
    ctx = dataclasses.replace(
        base_context,
        budgets=(
            BudgetStatus(
                category_id="cat-1",
                category_name="Lebensmittel",
                monthly_limit=Decimal("300"),
                actual_spent=Decimal("250"),
            ),
        ),
    )
    assert budget_overrun.evaluate(ctx) == []
