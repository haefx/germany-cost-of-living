import dataclasses
from decimal import Decimal

from analytics.insights.models import CategorySpending
from analytics.insights.rules import spending_increase


def _category(current: Decimal, average: Decimal) -> CategorySpending:
    return CategorySpending(
        category_id="cat-1",
        category_name="Freizeit",
        current_amount=current,
        trailing_average=average,
        trailing_history=(average, average, average),
    )


def test_fires_when_increase_exceeds_both_thresholds(base_context):
    ctx = dataclasses.replace(
        base_context, category_spending=(_category(Decimal("130"), Decimal("100")),)
    )
    insights = spending_increase.evaluate(ctx)
    assert len(insights) == 1


def test_does_not_fire_below_relative_threshold(base_context):
    # 10% increase, below the 25% relative threshold
    ctx = dataclasses.replace(
        base_context, category_spending=(_category(Decimal("110"), Decimal("100")),)
    )
    assert spending_increase.evaluate(ctx) == []


def test_does_not_fire_below_absolute_threshold_even_if_relative_is_high(base_context):
    # 100% relative increase but only 5 EUR absolute, below the noise floor
    ctx = dataclasses.replace(
        base_context, category_spending=(_category(Decimal("10"), Decimal("5")),)
    )
    assert spending_increase.evaluate(ctx) == []


def test_does_not_fire_with_no_trailing_history(base_context):
    ctx = dataclasses.replace(
        base_context, category_spending=(_category(Decimal("200"), Decimal("0")),)
    )
    assert spending_increase.evaluate(ctx) == []
