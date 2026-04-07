"""Kernlogik: Nettoeinkommen, verfügbares Einkommen, Kaufkraft und Sparprojektion."""

# Netto-Quoten je Steuerklasse (Näherung inkl. Sozialabgaben ~20%)
TAX_CLASS_RATES = {1: 0.670, 2: 0.670, 3: 0.755, 4: 0.670, 5: 0.545}

# Geschätzte Nettokosten pro Kind/Monat (nach Kindergeld ~250 €)
CHILD_COST_NET = 550


def net_income(gross: float, tax_class: int = 1) -> float:
    """Nettoeinkommen nach Steuerklasse (Pauschalschätzung)."""
    rate = TAX_CLASS_RATES.get(tax_class, 0.67)
    return round(gross * rate, 2)


def children_costs(num_children: int) -> float:
    """Gesamtkosten Kinder pro Monat (nach Kindergeld)."""
    return num_children * CHILD_COST_NET


def disposable_income(
    gross: float,
    rent: float,
    utilities: float,
    groceries: float,
    transport: float,
    tax_class: int = 1,
    num_children: int = 0,
) -> float:
    """Verfügbares Einkommen nach allen Fixkosten."""
    net = net_income(gross, tax_class)
    kids = children_costs(num_children)
    return round(net - rent - utilities - groceries - transport - kids, 2)


def affordability_score(disposable: float, net: float) -> tuple[str, str]:
    """
    Gibt (Label, Farbe) zurück basierend auf Anteil des verfügbaren Einkommens.
    Schwellenwerte: <10% kritisch, <25% eng, <45% mittel, sonst gut.
    """
    ratio = disposable / net if net > 0 else 0
    if ratio < 0.10:
        return "Kritisch", "#e74c3c"
    if ratio < 0.25:
        return "Eng", "#e67e22"
    if ratio < 0.45:
        return "Mittel", "#f1c40f"
    return "Gut", "#2ecc71"


def rent_burden_pct(rent: float, net: float) -> float:
    """Mietbelastungsquote in Prozent (Anteil Miete am Nettoeinkommen)."""
    return round((rent / net * 100) if net > 0 else 0, 1)


def savings_projection(
    monthly_savings: float,
    years: int = 10,
    annual_return: float = 0.04,
) -> list[dict]:
    """
    Zinseszins-Projektion für monatliches Sparen.
    Gibt Liste mit {Jahr, Eingezahlt, Zinsen, Gesamt} zurück.
    """
    monthly_rate = annual_return / 12
    total = 0.0
    deposited = 0.0
    result = []
    for month in range(1, years * 12 + 1):
        total = total * (1 + monthly_rate) + monthly_savings
        deposited += monthly_savings
        if month % 12 == 0:
            result.append({
                "Jahr": month // 12,
                "Eingezahlt": round(deposited, 2),
                "Zinsen": round(total - deposited, 2),
                "Gesamt": round(total, 2),
            })
    return result
