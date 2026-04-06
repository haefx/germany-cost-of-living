-- Germany Cost of Living Reality Check
-- Dokumentierte Abfragen

-- 1. Alle Städte mit aktuellem Medianlohn
SELECT c.name, c.state, s.median_gross, s.year
FROM cities c
JOIN salaries s ON s.city_id = c.id
WHERE s.year = (SELECT MAX(year) FROM salaries)
ORDER BY s.median_gross DESC;

-- 2. Durchschnittliche Kaltmiete pro Stadt (aktuelle Daten)
SELECT c.name, r.sqm_cold, r.avg_apartment_size,
       ROUND(r.sqm_cold * r.avg_apartment_size, 2) AS est_monthly_rent
FROM cities c
JOIN rent_prices r ON r.city_id = c.id
WHERE r.year = (SELECT MAX(year) FROM rent_prices)
ORDER BY r.sqm_cold DESC;

-- 3. Verfügbares Einkommen nach Fixkosten
SELECT
    c.name,
    s.median_gross,
    ROUND(r.sqm_cold * r.avg_apartment_size, 2)          AS rent,
    l.utilities_month,
    l.groceries_month,
    l.transport_month,
    ROUND(
        s.median_gross
        - (r.sqm_cold * r.avg_apartment_size)
        - l.utilities_month
        - l.groceries_month
        - l.transport_month,
        2
    ) AS disposable_income
FROM cities c
JOIN salaries    s ON s.city_id = c.id AND s.year = 2024
JOIN rent_prices r ON r.city_id = c.id AND r.year = 2024
JOIN living_costs l ON l.city_id = c.id AND l.year = 2024
ORDER BY disposable_income DESC;

-- 4. Kostenstruktur für Dashboard-Donut-Chart
SELECT
    c.name,
    ROUND(r.sqm_cold * r.avg_apartment_size, 2) AS rent,
    l.utilities_month,
    l.groceries_month,
    l.transport_month
FROM cities c
JOIN rent_prices r  ON r.city_id  = c.id AND r.year  = 2024
JOIN living_costs l ON l.city_id  = c.id AND l.year  = 2024;
