import dataclasses

from analytics.insights.rules import outdated_data


def test_fires_when_older_than_threshold(base_context):
    ctx = dataclasses.replace(
        base_context, reference_snapshot_age_days=600, reference_snapshot_max_age_days=548
    )
    assert len(outdated_data.evaluate(ctx)) == 1


def test_does_not_fire_within_threshold(base_context):
    ctx = dataclasses.replace(
        base_context, reference_snapshot_age_days=100, reference_snapshot_max_age_days=548
    )
    assert outdated_data.evaluate(ctx) == []


def test_does_not_fire_when_age_is_unknown(base_context):
    ctx = dataclasses.replace(base_context, reference_snapshot_age_days=None)
    assert outdated_data.evaluate(ctx) == []


def test_does_not_fire_exactly_at_threshold(base_context):
    ctx = dataclasses.replace(
        base_context, reference_snapshot_age_days=548, reference_snapshot_max_age_days=548
    )
    assert outdated_data.evaluate(ctx) == []
