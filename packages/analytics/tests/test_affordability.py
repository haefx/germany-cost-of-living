from decimal import Decimal

from analytics.affordability import affordability_level


def test_critical_below_ten_percent():
    assert affordability_level(Decimal("50"), Decimal("3000")) == "critical"


def test_tight_between_ten_and_twenty_five_percent():
    assert affordability_level(Decimal("500"), Decimal("3000")) == "tight"


def test_moderate_between_twenty_five_and_forty_five_percent():
    assert affordability_level(Decimal("1000"), Decimal("3000")) == "moderate"


def test_comfortable_above_forty_five_percent():
    assert affordability_level(Decimal("1600"), Decimal("3000")) == "comfortable"


def test_zero_net_income_is_critical():
    assert affordability_level(Decimal("0"), Decimal("0")) == "critical"
