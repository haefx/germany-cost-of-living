import dataclasses
from datetime import date
from decimal import Decimal

from analytics.insights.models import RecurringExpenseEntry
from analytics.insights.rules import duplicate_recurring


def test_fires_for_same_amount_and_similar_label(base_context):
    ctx = dataclasses.replace(
        base_context,
        recurring_expenses=(
            RecurringExpenseEntry(
                id="e1",
                category_id="cat-1",
                label="Netflix",
                amount=Decimal("9.99"),
                entry_date=date(2026, 6, 1),
                recurrence_rule_id="rule-1",
            ),
            RecurringExpenseEntry(
                id="e2",
                category_id="cat-1",
                label="Netflix Abo",
                amount=Decimal("9.99"),
                entry_date=date(2026, 6, 3),
                recurrence_rule_id="rule-2",
            ),
        ),
    )
    insights = duplicate_recurring.evaluate(ctx)
    assert len(insights) == 1


def test_does_not_fire_for_different_amounts(base_context):
    ctx = dataclasses.replace(
        base_context,
        recurring_expenses=(
            RecurringExpenseEntry(
                id="e1",
                category_id="cat-1",
                label="Netflix",
                amount=Decimal("9.99"),
                entry_date=date(2026, 6, 1),
                recurrence_rule_id="rule-1",
            ),
            RecurringExpenseEntry(
                id="e2",
                category_id="cat-1",
                label="Netflix",
                amount=Decimal("15.99"),
                entry_date=date(2026, 6, 3),
                recurrence_rule_id="rule-2",
            ),
        ),
    )
    assert duplicate_recurring.evaluate(ctx) == []


def test_does_not_fire_for_unrelated_labels(base_context):
    ctx = dataclasses.replace(
        base_context,
        recurring_expenses=(
            RecurringExpenseEntry(
                id="e1",
                category_id="cat-1",
                label="Netflix",
                amount=Decimal("9.99"),
                entry_date=date(2026, 6, 1),
                recurrence_rule_id="rule-1",
            ),
            RecurringExpenseEntry(
                id="e2",
                category_id="cat-2",
                label="Fitnessstudio",
                amount=Decimal("9.99"),
                entry_date=date(2026, 6, 3),
                recurrence_rule_id="rule-2",
            ),
        ),
    )
    assert duplicate_recurring.evaluate(ctx) == []


def test_same_recurrence_rule_is_never_flagged_against_itself(base_context):
    entry = RecurringExpenseEntry(
        id="e1",
        category_id="cat-1",
        label="Netflix",
        amount=Decimal("9.99"),
        entry_date=date(2026, 6, 1),
        recurrence_rule_id="rule-1",
    )
    ctx = dataclasses.replace(base_context, recurring_expenses=(entry, entry))
    assert duplicate_recurring.evaluate(ctx) == []
