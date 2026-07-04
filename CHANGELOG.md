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

## [0.1.0] - Streamlit prototype

- Initial prototype: Streamlit UI, SQLite storage, Numbeo-scraping-based cost
  data, flat tax-class net-income approximation. Superseded by the rebuild
  above.
