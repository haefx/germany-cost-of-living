from decimal import Decimal

from analytics.disposable_income import disposable_income, reference_household_disposable_income


def test_positive_disposable_income():
    assert disposable_income(Decimal("3000"), Decimal("2000")) == Decimal("1000")


def test_negative_disposable_income_is_allowed():
    # A negative result is a valid, meaningful signal (feeds negative_cash_flow),
    # not an error condition.
    assert disposable_income(Decimal("1500"), Decimal("2000")) == Decimal("-500")


def test_zero_expenses():
    assert disposable_income(Decimal("2000"), Decimal("0")) == Decimal("2000")


def test_reference_household_sums_all_cost_components():
    result = reference_household_disposable_income(
        net_income=Decimal("2800"),
        rent=Decimal("1000"),
        utilities=Decimal("200"),
        groceries=Decimal("350"),
        transport=Decimal("90"),
    )
    assert result == Decimal("1160")
