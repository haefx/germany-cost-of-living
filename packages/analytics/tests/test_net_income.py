from decimal import Decimal

import pytest

from analytics.net_income import NET_INCOME_ASSUMPTIONS_2026, estimate_net_income


def test_net_is_never_negative_for_typical_income():
    estimate = estimate_net_income(Decimal("3500"))
    assert estimate.net_monthly >= 0


def test_net_is_less_than_gross():
    estimate = estimate_net_income(Decimal("3500"))
    assert estimate.net_monthly < estimate.gross_monthly


def test_zero_gross_yields_zero_net():
    estimate = estimate_net_income(Decimal("0"))
    assert estimate.net_monthly == Decimal("0.00")
    assert estimate.income_tax_monthly == Decimal("0.00")
    assert estimate.social_insurance_monthly == Decimal("0.00")


def test_negative_gross_raises():
    with pytest.raises(ValueError):
        estimate_net_income(Decimal("-100"))


def test_higher_gross_yields_higher_net_monotonic():
    lower = estimate_net_income(Decimal("2500"))
    higher = estimate_net_income(Decimal("5000"))
    assert higher.net_monthly > lower.net_monthly


def test_below_basic_allowance_has_no_income_tax():
    # 800 EUR/month = 9,600 EUR/year, below the 12,000 EUR annual allowance,
    # even before subtracting social insurance.
    estimate = estimate_net_income(Decimal("800"))
    assert estimate.income_tax_monthly == Decimal("0.00")
    assert estimate.social_insurance_monthly > 0


def test_result_is_deterministic():
    first = estimate_net_income(Decimal("4123.45"))
    second = estimate_net_income(Decimal("4123.45"))
    assert first == second


def test_assumptions_are_surfaced_on_the_result():
    estimate = estimate_net_income(Decimal("3500"))
    assert len(estimate.assumptions) > 0
    assert estimate.year == NET_INCOME_ASSUMPTIONS_2026.year


def test_rounds_to_the_cent():
    estimate = estimate_net_income(Decimal("3333.33"))
    for value in (
        estimate.net_monthly,
        estimate.income_tax_monthly,
        estimate.social_insurance_monthly,
    ):
        assert value == value.quantize(Decimal("0.01"))
