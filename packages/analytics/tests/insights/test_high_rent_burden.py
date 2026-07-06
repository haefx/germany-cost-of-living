import dataclasses
from decimal import Decimal

from analytics.insights.rules import high_rent_burden


def test_fires_at_warning_threshold(base_context):
    ctx = dataclasses.replace(base_context, rent_amount=Decimal("900"), net_income=Decimal("3000"))
    insights = high_rent_burden.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].severity == "warning"


def test_fires_critical_above_forty_percent(base_context):
    ctx = dataclasses.replace(base_context, rent_amount=Decimal("1300"), net_income=Decimal("3000"))
    insights = high_rent_burden.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].severity == "critical"


def test_does_not_fire_below_threshold(base_context):
    ctx = dataclasses.replace(base_context, rent_amount=Decimal("500"), net_income=Decimal("3000"))
    assert high_rent_burden.evaluate(ctx) == []


def test_does_not_fire_without_net_income(base_context):
    ctx = dataclasses.replace(base_context, rent_amount=Decimal("900"), net_income=None)
    assert high_rent_burden.evaluate(ctx) == []


def test_does_not_fire_without_rent_amount(base_context):
    ctx = dataclasses.replace(base_context, rent_amount=None, net_income=Decimal("3000"))
    assert high_rent_burden.evaluate(ctx) == []
