import dataclasses
from decimal import Decimal

from analytics.insights.rules import negative_cash_flow


def test_fires_when_expenses_exceed_income(base_context):
    ctx = dataclasses.replace(
        base_context, total_income=Decimal("2000"), total_expenses=Decimal("2500")
    )
    insights = negative_cash_flow.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].severity == "critical"


def test_does_not_fire_when_income_equals_expenses(base_context):
    ctx = dataclasses.replace(
        base_context, total_income=Decimal("2000"), total_expenses=Decimal("2000")
    )
    assert negative_cash_flow.evaluate(ctx) == []


def test_does_not_fire_when_income_exceeds_expenses(base_context):
    ctx = dataclasses.replace(
        base_context, total_income=Decimal("3000"), total_expenses=Decimal("2000")
    )
    assert negative_cash_flow.evaluate(ctx) == []
