"""Runs every registered deterministic insight rule against a context and
returns a merged, sorted list. A single misbehaving rule cannot break the
response for the others — its exception is captured on the returned report
instead of propagating.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import ModuleType

from .models import Insight, InsightContext
from .rules import (
    budget_overrun,
    category_change,
    duplicate_recurring,
    high_rent_burden,
    missing_categories,
    missing_inputs,
    negative_cash_flow,
    outdated_data,
    savings_goal_delay,
    spending_increase,
)

logger = logging.getLogger(__name__)

_RULE_MODULES: tuple[ModuleType, ...] = (
    negative_cash_flow,
    budget_overrun,
    high_rent_burden,
    savings_goal_delay,
    duplicate_recurring,
    spending_increase,
    category_change,
    missing_categories,
    missing_inputs,
    outdated_data,
)

_SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class InsightReport:
    insights: tuple[Insight, ...]
    failed_rules: tuple[str, ...] = field(default_factory=tuple)


def run_all(ctx: InsightContext) -> InsightReport:
    insights: list[Insight] = []
    failed_rules: list[str] = []

    for module in _RULE_MODULES:
        try:
            insights.extend(module.evaluate(ctx))
        except Exception:
            logger.exception("Insight rule %s raised an exception", module.RULE_KEY)
            failed_rules.append(module.RULE_KEY)

    insights.sort(
        key=lambda insight: (
            _SEVERITY_ORDER.get(insight.severity, 99),
            -(insight.estimated_savings_max or 0),
        )
    )
    return InsightReport(insights=tuple(insights), failed_rules=tuple(failed_rules))
