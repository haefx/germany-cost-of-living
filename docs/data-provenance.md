# Data Provenance

This document describes exactly where every number displayed by the
application comes from, how fresh it is, and which figures are estimates.
The licensing side is covered in [`DATA_LICENSES.md`](../DATA_LICENSES.md).

## The one-sentence honest version

City comparison figures are a **hand-compiled 2023 reference snapshot**
modeled on the kind of data Destatis, the Bundesagentur für Arbeit, and the
BBSR Wohnatlas publish — they were **not** re-fetched from a live,
license-verified source for this release, and the UI labels them accordingly
(source name, reference year, and import date are shown on the Data sources
page and next to every city comparison).

## City reference dataset

File: [`data/reference/cities_reference_2023.csv`](../data/reference/cities_reference_2023.csv)
· Reference year: **2023** · Modeled-on sources: Destatis, Bundesagentur für
Arbeit, BBSR Wohnatlas

| City | State | Population | Median gross €/month | Cold rent €/m² | Groceries €/month | Transport €/month | Utilities €/month |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Berlin | Berlin | 3,645,000 | 3,850 | 16.50 | 380 | 95 | 230 |
| Hamburg | Hamburg | 1,841,000 | 4,100 | 17.80 | 390 | 109 | 240 |
| München | Bayern | 1,488,000 | 4,600 | 22.50 | 420 | 57 | 260 |
| Köln | Nordrhein-Westfalen | 1,084,000 | 3,750 | 15.20 | 370 | 103 | 225 |
| Frankfurt am Main | Hessen | 773,000 | 4,400 | 18.90 | 400 | 108 | 245 |
| Stuttgart | Baden-Württemberg | 626,000 | 4,250 | 17.40 | 390 | 93 | 235 |
| Leipzig | Sachsen | 620,000 | 3,100 | 10.20 | 330 | 66 | 190 |
| Düsseldorf | Nordrhein-Westfalen | 619,000 | 3,900 | 15.80 | 375 | 100 | 230 |
| Dortmund | Nordrhein-Westfalen | 588,000 | 3,300 | 10.80 | 340 | 95 | 195 |
| Nürnberg | Bayern | 515,000 | 3,700 | 13.50 | 355 | 98 | 210 |

An `avg_apartment_size` (m²) column and a flat 2023 inflation rate (5.9 %)
are also included per city; the pipeline's transform stage derives
`estimated_monthly_rent = sqm_cold × avg_apartment_size` rather than storing
a rent total directly.

### What these figures are

- Plausible, internally consistent 2023-era values for the ten largest
  German cities, carried over from the original prototype's seed data and
  reviewed for obvious outliers by the pipeline's validation stage.
- Attributed to Destatis / BA / BBSR **by style**: those are the institutions
  that publish this class of data, and a Phase 2 integration would fetch from
  them (see [`phase-2-roadmap.md`](phase-2-roadmap.md)).

### What they are not

- Not a redistribution of a specific licensed dataset.
- Not re-verified against a live source for this release.
- Not current-year figures — the reference year is 2023 and the UI says so.
  The insights engine even fires an "outdated reference data" notice based on
  the snapshot's age.

## How provenance is tracked structurally

The old prototype displayed figures with no provenance and had a genuine
data-year bug (one query hardcoded 2024 while the UI hardcoded 2023). The
rebuild fixes this structurally rather than by convention:

- Every pipeline run creates an **`import_runs`** row (source, status, row
  counts, timestamps). Loaded snapshots reference their run; history is never
  deleted.
- A run becomes visible to the application only when its **`published_at`**
  pointer is set, and publish is refused while error-severity validation
  findings exist. The API always reads the latest *published* run — there is
  no `MAX(year)` anywhere to drift.
- The validation stage records its findings in **`validation_results`**
  (severity, field, message) instead of silently clipping outliers the way
  the prototype did.
- The Data sources page in the UI surfaces the source name, reference
  period, import timestamp, and validation summary for the currently
  published run.

Pipeline commands: `make data-refresh` (full run), `make data-validate`
(extract + validate dry run, never loads or publishes), `make data-status`
(latest run + validation summary per source).

## Net-income estimate assumptions

The optional gross-to-net estimate in `packages/analytics` uses a versioned
assumption set, `NET_INCOME_ASSUMPTIONS_2026`
([`packages/analytics/analytics/net_income.py`](../packages/analytics/analytics/net_income.py)):
a simplified 5-band progressive-tax approximation plus a flat 20.5 %
social-insurance deduction. Every simplification (no Ehegattensplitting, no
tax classes, no contribution ceilings, no church tax) is spelled out in the
assumption set and surfaced to the user alongside any estimate.

⚠️ The 2026 rates and bracket bounds in that file are **plausible
approximations that have not been verified against authoritative
publications** (BMF, Sozialversicherungsentgeltverordnung). Verify before any
real-world use; the module's docstring carries the same warning. Users can
always enter their actual net income directly, which bypasses the estimate
entirely — that is the primary input path.

## Postal-code lookup

Postal codes are resolved to city/state names live via
[api.zippopotam.us](https://api.zippopotam.us). Responses are used
transiently and never stored. When the API is unreachable the lookup degrades
gracefully (manual city selection still works); a bundled offline dataset is
deferred to Phase 2.

## Demo data

Demo households are seeded with clearly synthetic example entries at
`POST /api/demo/start` and are deleted automatically after
`DEMO_HOUSEHOLD_TTL_HOURS` (default 24 h). Demo data never mixes with the
reference dataset or with registered users' data.
