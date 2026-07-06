"""Detects likely-duplicate recurring expenses: two separate recurring rules
with a near-identical label and the same amount (e.g. a subscription added
twice under slightly different names).
"""

from __future__ import annotations

import re
from decimal import Decimal

from ..models import Insight, InsightContext, RecurringExpenseEntry

RULE_KEY = "duplicate_recurring_expenses"


def _normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]", "", label.lower())


def evaluate(ctx: InsightContext) -> list[Insight]:
    insights: list[Insight] = []
    seen_pairs: set[frozenset[str]] = set()
    entries = list(ctx.recurring_expenses)

    for i, entry_a in enumerate(entries):
        for entry_b in entries[i + 1 :]:
            if entry_a.recurrence_rule_id == entry_b.recurrence_rule_id:
                continue
            if entry_a.amount != entry_b.amount:
                continue
            norm_a, norm_b = _normalize_label(entry_a.label), _normalize_label(entry_b.label)
            if not norm_a or not norm_b:
                continue
            if norm_a != norm_b and norm_a not in norm_b and norm_b not in norm_a:
                continue

            pair_key = frozenset({entry_a.id, entry_b.id})
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            insights.append(_build_insight(entry_a, entry_b))
    return insights


def _build_insight(entry_a: RecurringExpenseEntry, entry_b: RecurringExpenseEntry) -> Insight:
    return Insight(
        rule_key=RULE_KEY,
        severity="warning",
        title="Mögliche doppelte wiederkehrende Ausgabe",
        explanation=(
            f'"{entry_a.label}" und "{entry_b.label}" sind beide als wiederkehrend erfasst, '
            f"mit demselben Betrag ({entry_a.amount} €) und ähnlichem Namen. Das kann ein "
            "versehentlich doppelt angelegtes Abo sein."
        ),
        evidence={
            "entry_ids": [entry_a.id, entry_b.id],
            "labels": [entry_a.label, entry_b.label],
            "amount": str(entry_a.amount),
        },
        confidence="low",
        suggested_action=(
            "Prüfe, ob beide Einträge tatsächlich zu unterschiedlichen Verträgen gehören, "
            "oder ob einer davon gelöscht werden kann."
        ),
        assumptions=(
            "Erkennung basiert auf identischem Betrag und ähnlichem Namen, nicht auf einer "
            "Prüfung der tatsächlichen Verträge.",
        ),
        estimated_savings_min=Decimal("0"),
        estimated_savings_max=entry_a.amount,
    )
