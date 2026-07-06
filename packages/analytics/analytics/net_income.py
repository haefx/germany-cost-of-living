"""Optional gross-to-net income estimate.

This is a deliberately simplified, versioned approximation of German payroll
deductions. It exists only as a convenience for users who don't know their
net income offhand — the primary input everywhere else in the application is
the user's own entered net income, which always takes precedence and can
override this estimate.

This is NOT a payroll calculation, NOT tax advice, and does not reproduce the
official wage-tax formula (Section 32a EStG) or the real contribution-ceiling
rules for social insurance. See ``NET_INCOME_ASSUMPTIONS_2026.assumptions``
for the specific simplifications, all of which are surfaced to the user
alongside any estimate produced by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")


def _round_currency(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class TaxBracket:
    """A marginal-rate band applied to taxable annual income above ``lower_bound``."""

    lower_bound: Decimal
    upper_bound: Decimal | None  # None means "and above"
    marginal_rate: Decimal


@dataclass(frozen=True)
class NetIncomeAssumptions:
    year: int
    basic_allowance_annual: Decimal
    social_insurance_rate: Decimal
    brackets: tuple[TaxBracket, ...]
    assumptions: tuple[str, ...]


NET_INCOME_ASSUMPTIONS_2026 = NetIncomeAssumptions(
    year=2026,
    basic_allowance_annual=Decimal("12000"),
    social_insurance_rate=Decimal("0.205"),
    brackets=(
        TaxBracket(Decimal("0"), Decimal("12000"), Decimal("0.00")),
        TaxBracket(Decimal("12000"), Decimal("17000"), Decimal("0.14")),
        TaxBracket(Decimal("17000"), Decimal("66700"), Decimal("0.30")),
        TaxBracket(Decimal("66700"), Decimal("277800"), Decimal("0.42")),
        TaxBracket(Decimal("277800"), None, Decimal("0.45")),
    ),
    assumptions=(
        "Single-earner approximation: does not model spousal income splitting "
        "(Ehegattensplitting) or German tax classes (Steuerklasse).",
        "Social insurance is approximated as a flat 20.5% of gross income; the real "
        "contribution ceilings (Beitragsbemessungsgrenzen) for pension, unemployment, "
        "health, and long-term care insurance are not modeled, so deductions on "
        "high incomes are overestimated.",
        "Church tax (8-9% for registered members) is not included.",
        "Income tax brackets are a simplified 5-band approximation of the general shape "
        "of the German progressive schedule, not the official quadratic formula in "
        "Section 32a EStG.",
        "This is an illustrative estimate for planning purposes only. It is not a "
        "payroll calculation, a Lohnsteuerbescheinigung, or tax advice, and should be "
        "verified against a real payslip or a certified calculator before being relied on.",
    ),
)


@dataclass(frozen=True)
class NetIncomeEstimate:
    year: int
    gross_monthly: Decimal
    social_insurance_monthly: Decimal
    income_tax_monthly: Decimal
    net_monthly: Decimal
    assumptions: tuple[str, ...] = field(default_factory=tuple)


def _income_tax_annual(taxable_annual: Decimal, brackets: tuple[TaxBracket, ...]) -> Decimal:
    if taxable_annual <= 0:
        return Decimal("0")

    tax = Decimal("0")
    for bracket in brackets:
        upper = bracket.upper_bound if bracket.upper_bound is not None else taxable_annual
        if taxable_annual <= bracket.lower_bound:
            break
        slice_amount = min(taxable_annual, upper) - bracket.lower_bound
        if slice_amount > 0:
            tax += slice_amount * bracket.marginal_rate
    return tax


def estimate_net_income(
    gross_monthly: Decimal,
    assumptions: NetIncomeAssumptions = NET_INCOME_ASSUMPTIONS_2026,
) -> NetIncomeEstimate:
    """Estimate monthly net income from monthly gross income.

    Deterministic and monotonic (a higher gross always yields a higher or
    equal net), but explicitly approximate — see ``assumptions.assumptions``
    for what is simplified away.
    """
    if gross_monthly < 0:
        raise ValueError("gross_monthly must not be negative")

    gross_annual = gross_monthly * 12
    social_insurance_annual = gross_annual * assumptions.social_insurance_rate
    taxable_annual = max(
        Decimal("0"),
        gross_annual - social_insurance_annual - assumptions.basic_allowance_annual,
    )
    income_tax_annual = _income_tax_annual(taxable_annual, assumptions.brackets)

    net_annual = gross_annual - social_insurance_annual - income_tax_annual

    return NetIncomeEstimate(
        year=assumptions.year,
        gross_monthly=_round_currency(gross_monthly),
        social_insurance_monthly=_round_currency(social_insurance_annual / 12),
        income_tax_monthly=_round_currency(income_tax_annual / 12),
        net_monthly=_round_currency(net_annual / 12),
        assumptions=assumptions.assumptions,
    )
