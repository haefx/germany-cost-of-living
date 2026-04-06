-- Germany Cost of Living Reality Check
-- Database Schema

CREATE TABLE IF NOT EXISTS cities (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    state     TEXT    NOT NULL,
    population INTEGER
);

CREATE TABLE IF NOT EXISTS salaries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id      INTEGER NOT NULL REFERENCES cities(id),
    median_gross REAL    NOT NULL,  -- Median Bruttogehalt €/Monat
    year         INTEGER NOT NULL,
    source       TEXT                -- z.B. 'Destatis', 'Bundesagentur für Arbeit'
);

CREATE TABLE IF NOT EXISTS rent_prices (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id             INTEGER NOT NULL REFERENCES cities(id),
    sqm_cold            REAL    NOT NULL,  -- Kaltmiete €/m²
    avg_apartment_size  REAL,              -- Durchschnittsgröße m²
    year                INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS living_costs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id          INTEGER NOT NULL REFERENCES cities(id),
    groceries_month  REAL,   -- Lebensmittel €/Monat
    transport_month  REAL,   -- ÖPNV + Auto €/Monat
    utilities_month  REAL,   -- Nebenkosten €/Monat
    inflation_rate   REAL,   -- VPI % aktuell
    year             INTEGER NOT NULL
);
