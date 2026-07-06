import dataclasses
from decimal import Decimal

from analytics.insights.rules import missing_inputs


def test_fires_when_net_income_is_missing(base_context):
    ctx = dataclasses.replace(
        base_context, net_income=None, has_any_categories=True, has_any_budgets=True
    )
    insights = missing_inputs.evaluate(ctx)
    assert len(insights) == 1
    assert "Nettoeinkommen" in insights[0].evidence["missing_inputs"]


def test_fires_when_categories_are_missing(base_context):
    ctx = dataclasses.replace(
        base_context, net_income=Decimal("3000"), has_any_categories=False, has_any_budgets=True
    )
    assert len(missing_inputs.evaluate(ctx)) == 1


def test_does_not_fire_when_everything_is_present(base_context):
    ctx = dataclasses.replace(
        base_context, net_income=Decimal("3000"), has_any_categories=True, has_any_budgets=True
    )
    assert missing_inputs.evaluate(ctx) == []
