"""PLZ-Lookup und On-Demand Numbeo-Scraping für beliebige deutsche Städte."""

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}


def plz_to_city(plz: str) -> dict | None:
    """Gibt {'city': str, 'state': str} zurück oder None bei Fehler."""
    try:
        resp = requests.get(f"https://api.zippopotam.us/de/{plz.strip()}", timeout=5)
        if resp.status_code != 200:
            return None
        data = resp.json()
        place = data["places"][0]
        return {"city": place["place name"], "state": place["state"]}
    except Exception:
        return None


def _parse_numbeo_value(soup: BeautifulSoup, label: str) -> float | None:
    for row in soup.select("table.data_wide_table tr"):
        cells = row.find_all("td")
        if len(cells) >= 2 and label.lower() in cells[0].get_text().lower():
            text = (
                cells[1]
                .get_text(strip=True)
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


def fetch_city_costs(city_name: str) -> dict | None:
    """
    Scrapt Kostendaten von Numbeo für eine beliebige Stadt.
    Gibt None zurück wenn die Seite nicht gefunden wird oder Daten fehlen.
    """
    # Numbeo-Slug: Leerzeichen → Bindestrich, z.B. "Bad Salzuflen" → "Bad-Salzuflen"
    slug = "-".join(word.capitalize() for word in city_name.strip().split())
    url = f"https://www.numbeo.com/cost-of-living/in/{slug}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    transport  = _parse_numbeo_value(soup, "Monthly Public Transport Pass")
    apartment  = _parse_numbeo_value(soup, "1 Bedroom Apartment in City Centre")
    utilities  = _parse_numbeo_value(soup, "Basic (Electricity, Heating, Cooling, Water, Garbage)")
    milk       = _parse_numbeo_value(soup, "Milk (Regular")
    restaurant = _parse_numbeo_value(soup, "Meal, Inexpensive Restaurant")

    if not all([transport, apartment, utilities]):
        return {"error": f"Keine vollständigen Daten auf Numbeo für '{city_name}' gefunden."}

    apt_size = 70  # Standard-Wohnfläche falls nicht bekannt
    sqm_cold = round(apartment / apt_size, 2)

    # Groceries-Schätzung: Milchpreis als regionaler Kalibrierungsfaktor
    groceries = 350
    if milk:
        ratio = milk / 1.05  # DE-Durchschnitt Milch ~1.05 €
        groceries = round(350 * ratio, 2)

    return {
        "city": city_name,
        "sqm": sqm_cold,
        "apt_size": apt_size,
        "rent": round(apartment, 2),
        "groceries": max(150, min(groceries, 800)),
        "transport": round(transport, 2),
        "utilities": round(utilities, 2),
        "numbeo_url": url,
    }
