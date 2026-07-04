import dataclasses
from datetime import date
from decimal import Decimal

from analytics.insights.models import SavingsGoalStatus
from analytics.insights.rules import savings_goal_delay


def test_fires_when_contribution_rate_is_far_below_required(base_context):
    goal = SavingsGoalStatus(
        id="goal-1",
        name="Urlaub",
        target_amount=Decimal("2400"),
        current_amount=Decimal("0"),
        target_date=date(2026, 12, 1),  # 6 months from base_context month (2026-06)
        trailing_monthly_contribution_avg=Decimal("100"),  # needs 400/month, only doing 100
    )
    ctx = dataclasses.replace(base_context, savings_goals=(goal,))
    insights = savings_goal_delay.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].severity == "warning"


def test_does_not_fire_when_on_track(base_context):
    goal = SavingsGoalStatus(
        id="goal-1",
        name="Urlaub",
        target_amount=Decimal("2400"),
        current_amount=Decimal("0"),
        target_date=date(2026, 12, 1),
        trailing_monthly_contribution_avg=Decimal("400"),  # exactly the required rate
    )
    ctx = dataclasses.replace(base_context, savings_goals=(goal,))
    assert savings_goal_delay.evaluate(ctx) == []


def test_does_not_fire_when_goal_already_reached(base_context):
    goal = SavingsGoalStatus(
        id="goal-1",
        name="Urlaub",
        target_amount=Decimal("1000"),
        current_amount=Decimal("1000"),
        target_date=date(2026, 12, 1),
        trailing_monthly_contribution_avg=Decimal("0"),
    )
    ctx = dataclasses.replace(base_context, savings_goals=(goal,))
    assert savings_goal_delay.evaluate(ctx) == []


def test_does_not_fire_without_target_date(base_context):
    goal = SavingsGoalStatus(
        id="goal-1",
        name="Urlaub",
        target_amount=Decimal("2400"),
        current_amount=Decimal("0"),
        target_date=None,
        trailing_monthly_contribution_avg=Decimal("10"),
    )
    ctx = dataclasses.replace(base_context, savings_goals=(goal,))
    assert savings_goal_delay.evaluate(ctx) == []


def test_fires_critical_when_target_date_already_passed(base_context):
    goal = SavingsGoalStatus(
        id="goal-1",
        name="Urlaub",
        target_amount=Decimal("2400"),
        current_amount=Decimal("1000"),
        target_date=date(2026, 1, 1),  # before base_context month (2026-06)
        trailing_monthly_contribution_avg=Decimal("100"),
    )
    ctx = dataclasses.replace(base_context, savings_goals=(goal,))
    insights = savings_goal_delay.evaluate(ctx)
    assert len(insights) == 1
    assert insights[0].severity == "critical"
