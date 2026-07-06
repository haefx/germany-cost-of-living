# ADR-0003: Checked-in reference dataset instead of live scraping

- **Status**: accepted (2026-07)
- **Context**: source of city cost-of-living data for the Phase 1 rebuild

## Context

The prototype's primary data path was live HTML scraping of Numbeo
(BeautifulSoup against table selectors), silently falling back to a
hardcoded 2023 dictionary when scraping broke — with no visible distinction
between the two. This had three problems: scraping violates most sites'
terms of use, CSS-selector scraping breaks without notice, and the silent
fallback meant the app could show year-old data while implying it was fresh.

The honest alternatives were: integrate real government APIs (Destatis
GENESIS, Bundesagentur für Arbeit, BBSR) with license verification, or ship a
clearly labeled static reference dataset. A real API integration requires
per-source license review, registration/API keys for some sources, and
schema work per source — too much scope for Phase 1, and doing it hastily
would risk exactly the kind of overclaiming this project set out to avoid.

## Decision

Phase 1 ships a **hand-compiled reference snapshot**
(`data/reference/cities_reference_2023.csv`, ten cities, reference year
2023, derived from the prototype's seed figures) and is **honest about it
everywhere**: the UI shows source and reference year, `DATA_LICENSES.md` and
`docs/data-provenance.md` state plainly that the figures are modeled on
Destatis/BA/BBSR-style publications and were not re-fetched from a live,
license-verified source, and an insight rule flags the snapshot's age to
users.

At the same time, the pipeline is built as if the data were remote: an
extract-adapter interface (`LocalReferenceCsvAdapter` today, an HTTP adapter
in Phase 2) feeding validate → normalize → transform → load → publish stages
with retry/backoff, recorded validation findings, immutable import history,
and staged publication (`published_at`). Swapping in a real source touches
only the adapter.

## Alternatives considered

- **Keep Numbeo scraping** — rejected outright: terms-of-use problems,
  fragility, and the misleading silent fallback.
- **Integrate Destatis/BA/BBSR now** — right end state, wrong phase; on the
  roadmap with the license review it deserves.
- **Fabricate a "live government data" label over static data** — listed only
  to record that it was explicitly ruled out; the project's constraint is
  that no claim in the UI or docs may overstate what the system does.

## Consequences

- City comparisons are honest but dated (2023) until Phase 2; the UI says so
  rather than hiding it.
- The pipeline's operational features (retries, validation records, staged
  publish) run against a local file today, which looks over-engineered in
  isolation — it is the deliberate seam for the Phase 2 source swap.
- The prototype's data-year inconsistency class of bug is gone structurally:
  consumers read the latest *published* import run, never a hardcoded year.
