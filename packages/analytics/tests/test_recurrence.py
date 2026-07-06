from datetime import date

import pytest

from analytics.recurrence import RecurrenceRule, expand_occurrences


def test_monthly_recurrence_within_range():
    rule = RecurrenceRule(frequency="monthly", interval_count=1, start_date=date(2026, 1, 15))
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 4, 30))
    assert occurrences == [
        date(2026, 1, 15),
        date(2026, 2, 15),
        date(2026, 3, 15),
        date(2026, 4, 15),
    ]


def test_monthly_recurrence_handles_month_end_clamping():
    # Jan 31 start -> Feb has no 31st, should clamp to Feb 28 (2026 is not a leap year)
    rule = RecurrenceRule(frequency="monthly", interval_count=1, start_date=date(2026, 1, 31))
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 3, 31))
    assert occurrences == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)]


def test_weekly_recurrence():
    rule = RecurrenceRule(frequency="weekly", interval_count=1, start_date=date(2026, 1, 5))
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 1, 26))
    assert occurrences == [
        date(2026, 1, 5),
        date(2026, 1, 12),
        date(2026, 1, 19),
        date(2026, 1, 26),
    ]


def test_yearly_recurrence():
    rule = RecurrenceRule(frequency="yearly", interval_count=1, start_date=date(2024, 6, 1))
    occurrences = expand_occurrences(rule, date(2024, 1, 1), date(2027, 12, 31))
    assert occurrences == [date(2024, 6, 1), date(2025, 6, 1), date(2026, 6, 1), date(2027, 6, 1)]


def test_interval_count_greater_than_one():
    rule = RecurrenceRule(frequency="monthly", interval_count=3, start_date=date(2026, 1, 1))
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 12, 31))
    assert occurrences == [date(2026, 1, 1), date(2026, 4, 1), date(2026, 7, 1), date(2026, 10, 1)]


def test_no_occurrences_before_start_date():
    rule = RecurrenceRule(frequency="monthly", interval_count=1, start_date=date(2026, 6, 1))
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 5, 31))
    assert occurrences == []


def test_end_date_truncates_occurrences():
    rule = RecurrenceRule(
        frequency="monthly",
        interval_count=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 15),
    )
    occurrences = expand_occurrences(rule, date(2026, 1, 1), date(2026, 12, 31))
    assert occurrences == [date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)]


def test_range_starting_mid_series_only_returns_in_range_dates():
    rule = RecurrenceRule(frequency="monthly", interval_count=1, start_date=date(2026, 1, 1))
    occurrences = expand_occurrences(rule, date(2026, 3, 1), date(2026, 5, 31))
    assert occurrences == [date(2026, 3, 1), date(2026, 4, 1), date(2026, 5, 1)]


def test_invalid_interval_count_raises():
    rule = RecurrenceRule(frequency="monthly", interval_count=0, start_date=date(2026, 1, 1))
    with pytest.raises(ValueError):
        expand_occurrences(rule, date(2026, 1, 1), date(2026, 12, 31))


def test_invalid_range_raises():
    rule = RecurrenceRule(frequency="monthly", interval_count=1, start_date=date(2026, 1, 1))
    with pytest.raises(ValueError):
        expand_occurrences(rule, date(2026, 12, 31), date(2026, 1, 1))


def test_leap_day_yearly_recurrence_clamps_to_feb_28():
    rule = RecurrenceRule(frequency="yearly", interval_count=1, start_date=date(2024, 2, 29))
    occurrences = expand_occurrences(rule, date(2024, 1, 1), date(2026, 12, 31))
    assert occurrences == [date(2024, 2, 29), date(2025, 2, 28), date(2026, 2, 28)]
