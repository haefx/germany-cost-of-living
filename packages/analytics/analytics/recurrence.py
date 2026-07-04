"""Recurrence expansion: turn a recurrence rule into concrete occurrence dates.

Recurring income/expenses are stored as a rule (frequency + interval + start/
end date), not as pre-materialized rows for every future month. This module
is the single place that expands a rule into actual dates for a given
reporting window, used by budget/chart aggregation and by insight rules that
need to reason about "how many times has this recurred."
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import Literal

Frequency = Literal["weekly", "monthly", "yearly"]


@dataclass(frozen=True)
class RecurrenceRule:
    frequency: Frequency
    interval_count: int
    start_date: date
    end_date: date | None = None


def _add_months(source: date, months: int) -> date:
    total_month_index = source.month - 1 + months
    year = source.year + total_month_index // 12
    month = total_month_index % 12 + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def expand_occurrences(rule: RecurrenceRule, range_start: date, range_end: date) -> list[date]:
    """Return every occurrence date of ``rule`` within [range_start, range_end],
    inclusive on both ends. Empty list if the rule hasn't started yet, has
    already ended, or its interval never lands inside the window.
    """
    if rule.interval_count <= 0:
        raise ValueError("interval_count must be positive")
    if range_end < range_start:
        raise ValueError("range_end must not be before range_start")

    effective_end = min(range_end, rule.end_date) if rule.end_date else range_end
    if effective_end < rule.start_date or effective_end < range_start:
        return []

    occurrences: list[date] = []
    step = 0
    # Bound the loop generously (100k occurrences) so a malformed rule can't
    # spin forever; this is far beyond any realistic use.
    max_iterations = 100_000

    while step < max_iterations:
        current = _nth_occurrence(rule, step)
        if current > effective_end:
            break
        if current >= range_start:
            occurrences.append(current)
        step += 1

    return occurrences


def _nth_occurrence(rule: RecurrenceRule, step: int) -> date:
    offset = step * rule.interval_count
    if rule.frequency == "weekly":
        return date.fromordinal(rule.start_date.toordinal() + 7 * offset)
    if rule.frequency == "monthly":
        return _add_months(rule.start_date, offset)
    # yearly
    try:
        return rule.start_date.replace(year=rule.start_date.year + offset)
    except ValueError:
        # Feb 29 start date landing on a non-leap target year.
        return date(rule.start_date.year + offset, 2, 28)
