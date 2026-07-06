# Initial Audit

This document records the state of the original Streamlit prototype before
the rebuild, and the specific problems that motivated it. It is kept as a
historical record rather than deleted once the rebuild lands, since the
reasoning behind an architecture decision is easy to lose otherwise.

## What existed

A single-page Streamlit application (~1,150 lines total) backed by SQLite:

- `app/streamlit_app.py` — sidebar inputs (postal code, gross salary, tax
  class, household size, living space, savings-rate assumptions) and three
  tabs (household breakdown, city comparison, savings projection).
- `app/components.py` — Plotly chart builders.
- `src/calculator.py`, `src/lookup.py`, `src/pipeline.py`, `src/db.py`,
  `src/seed_data.py` — calculation and data-access helpers.
- `sql/schema.sql`, `sql/queries.sql` — a flat SQLite schema and reference
  queries.

## Specific problems identified

1. **Net income was a flat percentage table, not a real calculation.**
   `src/calculator.py` defined `TAX_CLASS_RATES = {1: 0.670, 2: 0.670, 3: 0.755,
   4: 0.670, 5: 0.545}` and computed net income as `gross * rate`, with no
   year attached to the assumption and no indication in the UI that this was
   an approximation rather than a real payroll calculation.

2. **The core cost-of-living data source was live HTML scraping.**
   `src/lookup.py` and `src/pipeline.py` scraped Numbeo
   (`BeautifulSoup` against `table.data_wide_table` selectors) as the primary
   data path, silently falling back to a hardcoded `FALLBACK` dict of 2023
   figures when scraping failed — with no UI distinction between "just
   scraped" and "hardcoded fallback from over a year ago."

3. **A real data-year inconsistency.** `sql/queries.sql` hardcoded
   `year = 2024` in one reference query, while `app/streamlit_app.py` and
   `app/components.py` hardcoded `year = 2023` in the equivalent live
   queries. Depending on which code path executed, the app could silently
   compare different years' data as if it were consistent.

4. **Business logic duplicated across layers.** `app/components.py`'s
   `waterfall_chart` recomputed disposable income inline instead of calling
   `src/calculator.py::disposable_income`, and its `gauge_chart` duplicated
   the bucket thresholds from `calculator.py::affordability_score`. A change
   to the formula in one place would not have propagated to the other.

5. **No provenance or freshness signal for public data.** Rent, salary, and
   living-cost figures were displayed without a source citation, reference
   period, or "last updated" indicator visible to the user.

6. **No tests, CI, or migrations.** No `tests/` directory, no
   `.github/workflows/`, and the schema was a static `sql/schema.sql` applied
   via `executescript` rather than versioned migrations.

7. **No authentication or ownership model.** The prototype had a single
   implicit household with no concept of separate users or data isolation.

8. **Sparse documentation.** The README ended with a literal
   `TODO: Kurzer Abschnitt über SQL Joins, Pandas Cleaning-Herausforderungen,
   Datenqualität.` placeholder.

## What was reused

- The ten-city reference figures from `src/seed_data.py` (population, salary,
  rent, living-cost estimates attributed to Destatis / Bundesagentur für
  Arbeit / BBSR Wohnatlas) became the basis for the new, honestly-labeled
  reference dataset — see [`docs/data-provenance.md`](data-provenance.md).
- The postal-code lookup via the free [zippopotam.us](https://api.zippopotam.us)
  API was kept, since it is a legitimate public API rather than scraping.
- The chart color palette and the general shape of the three original views
  (household breakdown, city comparison, savings projection) informed the
  new dashboard's information architecture, without copying the Streamlit
  layout itself.

## What was rebuilt from scratch

Everything else: the net-income estimate, the data pipeline, the database
schema and migrations, authentication and ownership, the insights engine, and
the entire frontend. See [`docs/architecture/overview.md`](architecture/overview.md)
for the resulting design and [`docs/phase-2-roadmap.md`](phase-2-roadmap.md)
for what is intentionally deferred.
