"""ETL Pipeline — lädt echte Daten von Numbeo, bereinigt sie und schreibt sie in die SQLite-DB."""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from db import init_db, get_connection

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

# Numbeo-Stadtnames (URL-Slug)
NUMBEO_SLUGS = {
    "Berlin":              "Berlin",
    "Hamburg":             "Hamburg",
    "München":             "Munich",
    "Köln":                "Cologne",
    "Frankfurt am Main":   "Frankfurt",
    "Stuttgart":           "Stuttgart",
    "Düsseldorf":          "Dusseldorf",
    "Leipzig":             "Leipzig",
    "Dortmund":            "Dortmund",
    "Nürnberg":            "Nuremberg",
}

# Fallback-Daten (Destatis / BA 2023) falls Scraping fehlschlägt
FALLBACK = {
    "Berlin":              dict(salary=3850, sqm=16.5, apt_size=72, groceries=380, transport=95,  utilities=230),
    "Hamburg":             dict(salary=4100, sqm=17.8, apt_size=70, groceries=390, transport=109, utilities=240),
    "München":             dict(salary=4600, sqm=22.5, apt_size=68, groceries=420, transport=57,  utilities=260),
    "Köln":                dict(salary=3750, sqm=15.2, apt_size=72, groceries=370, transport=103, utilities=225),
    "Frankfurt am Main":   dict(salary=4400, sqm=18.9, apt_size=68, groceries=400, transport=108, utilities=245),
    "Stuttgart":           dict(salary=4250, sqm=17.4, apt_size=70, groceries=390, transport=93,  utilities=235),
    "Düsseldorf":          dict(salary=3900, sqm=15.8, apt_size=71, groceries=375, transport=100, utilities=230),
    "Leipzig":             dict(salary=3100, sqm=10.2, apt_size=75, groceries=330, transport=66,  utilities=190),
    "Dortmund":            dict(salary=3300, sqm=10.8, apt_size=74, groceries=340, transport=95,  utilities=195),
    "Nürnberg":            dict(salary=3700, sqm=13.5, apt_size=72, groceries=355, transport=98,  utilities=210),
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}


def _parse_numbeo_value(soup: BeautifulSoup, label: str):
    """Sucht einen Numbeo-Kostenpunkt anhand des Labels."""
    for row in soup.select("table.data_wide_table tr"):
        cells = row.find_all("td")
        if len(cells) >= 2 and label.lower() in cells[0].get_text().lower():
            text = (
                cells[1].get_text(strip=True)
                .replace("\xa0", " ")
                .replace(",", "")
                .replace("€", "")
                .strip()
            )
            try:
                return float(text.split()[0])
            except (ValueError, IndexError):
                pass
    return None


def fetch_numbeo(city_name: str):
    """Scrapt Kostendaten von Numbeo für eine Stadt. Gibt None bei Fehler zurück."""
    slug = NUMBEO_SLUGS.get(city_name)
    if not slug:
        return None
    url = f"https://www.numbeo.com/cost-of-living/in/{slug}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [Numbeo] Anfrage fehlgeschlagen für {city_name}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    transport   = _parse_numbeo_value(soup, "Monthly Public Transport Pass")
    apartment   = _parse_numbeo_value(soup, "1 Bedroom Apartment in City Centre")
    utilities   = _parse_numbeo_value(soup, "Basic Utilities")
    # Groceries: Milk als Proxy für Preisniveau, sonst Fallback
    milk        = _parse_numbeo_value(soup, "Milk (Regular")

    if not all([transport, apartment, utilities]):
        print(f"  [Numbeo] Unvollständige Daten für {city_name}, nutze Fallback.")
        return None

    apt_size = FALLBACK[city_name]["apt_size"]
    sqm_cold = round(apartment / apt_size, 2)
    # Groceries: Numbeo-Milchpreis als Kalibrierung, sonst Fallback-Wert
    groceries = FALLBACK[city_name]["groceries"]
    if milk:
        ratio = milk / 1.05  # DE-Durchschnitt Milch ~1.05€
        groceries = round(FALLBACK[city_name]["groceries"] * ratio, 2)

    return dict(
        salary=FALLBACK[city_name]["salary"],  # Gehalt von BA-Daten
        sqm=sqm_cold,
        apt_size=apt_size,
        groceries=groceries,
        transport=round(transport, 2),
        utilities=round(utilities, 2),
    )


def extract() -> pd.DataFrame:
    """Holt Daten von Numbeo, fällt auf Fallback zurück wenn nötig."""
    records = []
    for name, state, pop in CITIES:
        print(f"Lade Daten für {name}...")
        data = fetch_numbeo(name)
        if data is None:
            print(f"  → Fallback-Daten für {name}")
            data = FALLBACK[name]
        records.append({
            "city":      name,
            "state":     state,
            "pop":       pop,
            **data,
        })
    return pd.DataFrame(records)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt und normalisiert den DataFrame."""
    df = df.copy()
    df["sqm"]        = df["sqm"].clip(lower=5, upper=50).round(2)
    df["groceries"]  = df["groceries"].clip(lower=100, upper=1000).round(2)
    df["transport"]  = df["transport"].clip(lower=30, upper=250).round(2)
    df["utilities"]  = df["utilities"].clip(lower=100, upper=500).round(2)
    df["salary"]     = df["salary"].clip(lower=1500, upper=10000).round(2)
    df = df.dropna(subset=["city", "sqm", "salary"])
    return df


def load(df: pd.DataFrame) -> None:
    """Schreibt den sauberen DataFrame in die SQLite-DB."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        DELETE FROM living_costs;
        DELETE FROM rent_prices;
        DELETE FROM salaries;
        DELETE FROM cities;
        DELETE FROM sqlite_sequence;
    """)

    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO cities (name, state, population) VALUES (?, ?, ?)",
            (row["city"], row["state"], int(row["pop"]))
        )
        city_id = cur.lastrowid

        cur.execute(
            "INSERT INTO salaries (city_id, median_gross, year, source) VALUES (?, ?, 2023, ?)",
            (city_id, row["salary"], "Bundesagentur für Arbeit / Destatis 2023")
        )
        cur.execute(
            "INSERT INTO rent_prices (city_id, sqm_cold, avg_apartment_size, year) VALUES (?, ?, ?, 2023)",
            (city_id, row["sqm"], row["apt_size"])
        )
        cur.execute(
            """INSERT INTO living_costs
               (city_id, groceries_month, transport_month, utilities_month, inflation_rate, year)
               VALUES (?, ?, ?, ?, 5.9, 2023)""",
            (city_id, row["groceries"], row["transport"], row["utilities"])
        )

    conn.commit()
    conn.close()
    print(f"\nLade abgeschlossen: {len(df)} Städte in die DB geschrieben.")


def run():
    print("Initialisiere Datenbank...")
    init_db()
    print("Extrahiere Daten...")
    raw = extract()
    print("\nBereinige Daten...")
    clean = transform(raw)
    print("Schreibe in DB...")
    load(clean)
    print("Pipeline abgeschlossen.")


if __name__ == "__main__":
    run()
