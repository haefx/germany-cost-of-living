import dataclasses
from decimal import Decimal

from analytics.insights.rules import missing_categories


def test_fires_above_count_threshold(base_context):
    ctx = dataclasses.replace(
        base_context, uncategorized_expense_count=5, uncategorized_expense_amount=Decimal("10")
    )
    assert len(missing_categories.evaluate(ctx)) == 1


def test_fires_above_amount_threshold(base_context):
    ctx = dataclasses.replace(
        base_context, uncategorized_expense_count=1, uncategorized_expense_amount=Decimal("80")
    )
    assert len(missing_categories.evaluate(ctx)) == 1


def test_does_not_fire_below_both_thresholds(base_context):
    ctx = dataclasses.replace(
        base_context, uncategorized_expense_count=1, uncategorized_expense_amount=Decimal("10")
    )
    assert missing_categories.evaluate(ctx) == []
