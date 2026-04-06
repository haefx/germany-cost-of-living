"""Kernlogik: Verfügbares Einkommen und Kaufkraft-Score berechnen."""


def net_income(gross: float, tax_class: int = 1) -> float:
    """Grobes Nettoeinkommen nach Steuerklasse (Näherung)."""
    # TODO: genaue Berechnung mit Lohnsteuer + SV-Beiträgen
    rates = {1: 0.67, 3: 0.75, 4: 0.67}
    return round(gross * rates.get(tax_class, 0.67), 2)


def disposable_income(
    gross: float,
    rent: float,
    utilities: float,
    groceries: float,
    transport: float,
    tax_class: int = 1,
) -> float:
    net = net_income(gross, tax_class)
    return round(net - rent - utilities - groceries - transport, 2)


def affordability_score(disposable: float, median_net: float) -> str:
    """Gibt 'Arm', 'Mittel' oder 'Gut' zurück basierend auf Kaufkraftindex."""
    ratio = disposable / median_net if median_net else 0
    if ratio < 0.2:
        return "Arm"
    if ratio < 0.5:
        return "Mittel"
    return "Gut"
