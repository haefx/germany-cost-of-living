"""Seed-Skript: Befüllt die DB mit realistischen Daten für 10 deutsche Städte."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cost_of_living.db")

CITIES = [
    ("Berlin", "Berlin", 3645000),
    ("Hamburg", "Hamburg", 1841000),
    ("München", "Bayern", 1488000),
    ("Köln", "Nordrhein-Westfalen", 1084000),
    ("Frankfurt am Main", "Hessen", 773000),
    ("Stuttgart", "Baden-Württemberg", 626000),
    ("Düsseldorf", "Nordrhein-Westfalen", 619000),
    ("Leipzig", "Sachsen", 620000),
    ("Dortmund", "Nordrhein-Westfalen", 588000),
    ("Nürnberg", "Bayern", 515000),
]

# Quellen: Destatis 2023, BBSR Wohnatlas 2023, Bundesagentur für Arbeit 2023
SALARIES = {
    "Berlin":              3850,
    "Hamburg":             4100,
    "München":             4600,
    "Köln":                3750,
    "Frankfurt am Main":   4400,
    "Stuttgart":           4250,
    "Düsseldorf":          3900,
    "Leipzig":             3100,
    "Dortmund":            3300,
    "Nürnberg":            3700,
}

# Kaltmiete €/m², Durchschnittswohnung m²
RENT = {
    "Berlin":              (16.5, 72),
    "Hamburg":             (17.8, 70),
    "München":             (22.5, 68),
    "Köln":                (15.2, 72),
    "Frankfurt am Main":   (18.9, 68),
    "Stuttgart":           (17.4, 70),
    "Düsseldorf":          (15.8, 71),
    "Leipzig":             (10.2, 75),
    "Dortmund":            (10.8, 74),
    "Nürnberg":            (13.5, 72),
}

# Lebensmittel, ÖPNV/Mobilität, Nebenkosten (€/Monat), Inflationsrate (%)
LIVING_COSTS = {
    "Berlin":              (380, 95,  230, 5.9),
    "Hamburg":             (390, 109, 240, 5.9),
    "München":             (420, 57,  260, 5.9),
    "Köln":                (370, 103, 225, 5.9),
    "Frankfurt am Main":   (400, 108, 245, 5.9),
    "Stuttgart":           (390, 93,  235, 5.9),
    "Düsseldorf":          (375, 100, 230, 5.9),
    "Leipzig":             (330, 66,  190, 5.9),
    "Dortmund":            (340, 95,  195, 5.9),
    "Nürnberg":            (355, 98,  210, 5.9),
}


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Bestehende Daten leeren
    cur.executescript("""
        DELETE FROM living_costs;
        DELETE FROM rent_prices;
        DELETE FROM salaries;
        DELETE FROM cities;
        DELETE FROM sqlite_sequence;
    """)

    city_ids = {}
    for name, state, pop in CITIES:
        cur.execute(
            "INSERT INTO cities (name, state, population) VALUES (?, ?, ?)",
            (name, state, pop)
        )
        city_ids[name] = cur.lastrowid

    for name, city_id in city_ids.items():
        cur.execute(
            "INSERT INTO salaries (city_id, median_gross, year, source) VALUES (?, ?, ?, ?)",
            (city_id, SALARIES[name], 2023, "Bundesagentur für Arbeit / Destatis")
        )
        sqm, size = RENT[name]
        cur.execute(
            "INSERT INTO rent_prices (city_id, sqm_cold, avg_apartment_size, year) VALUES (?, ?, ?, ?)",
            (city_id, sqm, size, 2023)
        )
        groc, transp, util, infl = LIVING_COSTS[name]
        cur.execute(
            "INSERT INTO living_costs (city_id, groceries_month, transport_month, utilities_month, inflation_rate, year) VALUES (?, ?, ?, ?, ?, ?)",
            (city_id, groc, transp, util, infl, 2023)
        )

    conn.commit()
    conn.close()
    print(f"Seed abgeschlossen: {len(CITIES)} Städte eingetragen.")


if __name__ == "__main__":
    seed()
