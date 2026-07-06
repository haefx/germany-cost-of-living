from decimal import Decimal

from analytics.rent_burden import rent_burden_level, rent_burden_pct


def test_typical_rent_burden():
    assert rent_burden_pct(Decimal("900"), Decimal("3000")) == Decimal("30.0")


def test_zero_net_income_returns_zero_not_error():
    assert rent_burden_pct(Decimal("900"), Decimal("0")) == Decimal("0.0")


def test_negative_net_income_returns_zero():
    assert rent_burden_pct(Decimal("900"), Decimal("-100")) == Decimal("0.0")


def test_level_ok_below_warning_threshold():
    assert rent_burden_level(Decimal("29.9")) == "ok"


def test_level_warning_at_boundary():
    assert rent_burden_level(Decimal("30.0")) == "warning"


def test_level_critical_at_boundary():
    assert rent_burden_level(Decimal("40.0")) == "critical"


def test_level_critical_above_boundary():
    assert rent_burden_level(Decimal("55.0")) == "critical"
