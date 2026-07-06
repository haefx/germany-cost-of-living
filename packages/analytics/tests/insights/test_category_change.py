import dataclasses
from decimal import Decimal

from analytics.insights.models import CategorySpending
from analytics.insights.rules import category_change


def test_fires_when_share_deviates_sharply(base_context):
    # Historically ~10% of total spend, now 40% of total spend.
    ctx = dataclasses.replace(
        base_context,
        total_expenses=Decimal("1000"),
        trailing_total_expenses=(Decimal("1000"), Decimal("1000"), Decimal("1000")),
        category_spending=(
            CategorySpending(
                category_id="cat-1",
                category_name="Freizeit",
                current_amount=Decimal("400"),
                trailing_average=Decimal("100"),
                trailing_history=(Decimal("100"), Decimal("100"), Decimal("100")),
            ),
        ),
    )
    insights = category_change.evaluate(ctx)
    assert len(insights) == 1


def test_does_not_fire_when_share_is_stable(base_context):
    ctx = dataclasses.replace(
        base_context,
        total_expenses=Decimal("1000"),
        trailing_total_expenses=(Decimal("1000"), Decimal("1000"), Decimal("1000")),
        category_spending=(
            CategorySpending(
                category_id="cat-1",
                category_name="Freizeit",
                current_amount=Decimal("100"),
                trailing_average=Decimal("100"),
                trailing_history=(Decimal("100"), Decimal("100"), Decimal("100")),
            ),
        ),
    )
    assert category_change.evaluate(ctx) == []


def test_does_not_fire_with_insufficient_history(base_context):
    ctx = dataclasses.replace(
        base_context,
        total_expenses=Decimal("1000"),
        trailing_total_expenses=(Decimal("1000"),),
        category_spending=(
            CategorySpending(
                category_id="cat-1",
                category_name="Freizeit",
                current_amount=Decimal("400"),
                trailing_average=Decimal("100"),
                trailing_history=(Decimal("100"),),
            ),
        ),
    )
    assert category_change.evaluate(ctx) == []


def test_does_not_fire_when_total_expenses_is_zero(base_context):
    ctx = dataclasses.replace(base_context, total_expenses=Decimal("0"))
    assert category_change.evaluate(ctx) == []
