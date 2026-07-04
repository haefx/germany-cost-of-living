from decimal import Decimal

import pytest

from analytics.savings_projection import project_savings


def test_zero_years_returns_empty_list():
    assert project_savings(Decimal("100"), years=0) == []


def test_zero_contribution_yields_all_zero():
    results = project_savings(Decimal("0"), years=2)
    assert all(r.deposited == 0 and r.total == 0 for r in results)


def test_zero_growth_rate_means_deposited_equals_total():
    results = project_savings(Decimal("200"), years=3, annual_growth_rate=Decimal("0"))
    for r in results:
        assert r.growth == Decimal("0.00")
        assert r.total == r.deposited


def test_deposited_plus_growth_equals_total_exactly():
    results = project_savings(Decimal("250"), years=5, annual_growth_rate=Decimal("0.04"))
    for r in results:
        assert r.deposited + r.growth == r.total


def test_deposited_grows_linearly_with_years():
    results = project_savings(Decimal("100"), years=4)
    assert results[0].deposited == Decimal("1200.00")
    assert results[3].deposited == Decimal("4800.00")


def test_positive_growth_rate_increases_total_over_pure_deposits():
    with_growth = project_savings(Decimal("200"), years=5, annual_growth_rate=Decimal("0.04"))
    without_growth = project_savings(Decimal("200"), years=5, annual_growth_rate=Decimal("0"))
    assert with_growth[-1].total > without_growth[-1].total


def test_negative_contribution_raises():
    with pytest.raises(ValueError):
        project_savings(Decimal("-10"), years=1)


def test_negative_years_raises():
    with pytest.raises(ValueError):
        project_savings(Decimal("10"), years=-1)


def test_negative_growth_rate_raises():
    with pytest.raises(ValueError):
        project_savings(Decimal("10"), years=1, annual_growth_rate=Decimal("-0.01"))


def test_inflation_adjustment_reduces_total_when_requested():
    results = project_savings(
        Decimal("200"),
        years=5,
        annual_growth_rate=Decimal("0.04"),
        annual_inflation_rate=Decimal("0.02"),
    )
    last = results[-1]
    assert last.total_inflation_adjusted is not None
    assert last.total_inflation_adjusted < last.total


def test_inflation_adjustment_is_none_when_not_requested():
    results = project_savings(Decimal("200"), years=2)
    assert all(r.total_inflation_adjusted is None for r in results)
