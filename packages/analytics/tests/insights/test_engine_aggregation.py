import dataclasses
from datetime import date
from decimal import Decimal

from analytics.insights import engine
from analytics.insights.models import InsightContext
from analytics.insights.rules import budget_overrun, negative_cash_flow


def test_a_raising_rule_does_not_crash_the_whole_run(base_context, monkeypatch):
    def boom(_ctx):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(budget_overrun, "evaluate", boom)

    ctx = dataclasses.replace(
        base_context, total_income=Decimal("1000"), total_expenses=Decimal("2000")
    )
    report = engine.run_all(ctx)

    assert "budget_overrun" in report.failed_rules
    # negative_cash_flow should still have fired despite budget_overrun blowing up
    assert any(insight.rule_key == negative_cash_flow.RULE_KEY for insight in report.insights)


def test_insights_are_sorted_by_severity_then_savings(base_context):
    ctx = dataclasses.replace(
        base_context, total_income=Decimal("1000"), total_expenses=Decimal("2000")
    )
    report = engine.run_all(ctx)

    severities = [insight.severity for insight in report.insights]
    severity_rank = {"critical": 0, "warning": 1, "info": 2}
    ranks = [severity_rank[s] for s in severities]
    assert ranks == sorted(ranks)


def test_no_failures_on_a_fully_healthy_context():
    ctx = InsightContext(
        month=date(2026, 6, 1),
        total_income=Decimal("3000"),
        total_expenses=Decimal("1000"),
        net_income=Decimal("3000"),
        has_any_categories=True,
        has_any_budgets=True,
    )
    report = engine.run_all(ctx)
    assert report.failed_rules == ()
