# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Rebuilt the project from a single-file Streamlit prototype into a Next.js
  (frontend) + FastAPI (backend) + PostgreSQL application. See
  [`docs/initial-audit.md`](docs/initial-audit.md) for the audit that
  motivated the rebuild and [`docs/phase-2-roadmap.md`](docs/phase-2-roadmap.md)
  for what is intentionally not yet included.
- Net income is now user-entered as the primary input, with an optional,
  versioned, clearly labeled estimate (`NET_INCOME_ASSUMPTIONS_2026`)
  replacing the prototype's flat per-tax-class percentages.
- City cost-of-living data now comes from a checked-in, honestly labeled
  2023 reference snapshot with a full ETL pipeline and staged publication,
  replacing live Numbeo HTML scraping with a silent hardcoded fallback.

### Added

- Email/password authentication (fastapi-users, Argon2id, database-backed
  revocable sessions) and anonymous demo households with automatic expiry.
- Per-user ownership enforcement on every query, with a parametrized
  cross-user isolation test suite.
- Household finance CRUD: income, expenses, categories, recurrence rules,
  budgets, savings goals with contribution ledgers; CSV import/export and
  full account export/deletion.
- Deterministic insights engine with ten rule-based checks (no AI).
- City comparison across ten German cities with visible data provenance
  (source, reference year, import run, validation findings).
- Postal-code lookup via zippopotam.us with graceful degradation.
- Test suites: 88 analytics tests, 81 API integration tests against real
  PostgreSQL; CI workflows for backend, frontend, and Docker builds with
  OpenAPI/type drift checks.
- Documentation: architecture overview, three ADRs, data provenance,
  Phase 2 roadmap, initial audit.

## [0.1.0] - Streamlit prototype

- Initial prototype: Streamlit UI, SQLite storage, Numbeo-scraping-based cost
  data, flat tax-class net-income approximation. Superseded by the rebuild
  above.
