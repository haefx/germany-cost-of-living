# ADR-0001: Next.js + FastAPI + PostgreSQL instead of extending Streamlit

- **Status**: accepted (2026-07)
- **Context**: Phase 1 rebuild of the Streamlit/SQLite prototype

## Context

The prototype was a single-page Streamlit app over SQLite. The rebuild's
goals — authenticated multi-user accounts, per-user data isolation, a
mobile-capable dashboard, tested domain logic, and versioned migrations —
pushed against Streamlit's design in fundamental ways: no real routing or
auth primitives, whole-script rerun execution model, server-rendered widgets
with limited control over interaction patterns, and no natural place for an
API contract that could be tested independently of the UI.

## Decision

Rebuild as three units:

- **Next.js 16 (App Router, TypeScript strict)** for the frontend. Server
  components + a typed fetch layer against the API; Tailwind v4 and Radix
  primitives instead of a heavyweight component framework; TanStack Query for
  server state; Recharts for charts.
- **FastAPI (async SQLAlchemy 2, Alembic)** for the backend. Python was kept
  deliberately: the domain calculations from the prototype remained Python,
  the ecosystem for the data-pipeline work is Python, and it keeps one
  backend language across API and pipeline.
- **PostgreSQL** instead of SQLite: real migrations, FK cascade behavior the
  account-deletion and demo-expiry features rely on, and concurrent access
  for multiple sessions.
- **`packages/analytics` as a standalone Python package** with zero framework
  imports, so the financial math is unit-testable without a database and has
  exactly one implementation (the prototype had chart code re-implementing
  calculator logic).
- **npm workspaces + a `packages/shared` OpenAPI snapshot** to bridge the
  Python/TypeScript boundary with generated types and CI drift checks in both
  directions, since no runtime code can be shared across the two languages.

## Alternatives considered

- **Keep Streamlit, add auth via a wrapper** — rejected: auth wrappers around
  Streamlit are session hacks, and the rerun model makes a CRUD-heavy,
  form-heavy app awkward; none of the audit's structural problems would have
  been addressed.
- **Django (+ templates or DRF)** — viable, but FastAPI's Pydantic-first
  contract generates the OpenAPI schema the typed frontend depends on, and
  async SQLAlchemy fits the small-service shape better than Django's ORM
  here.
- **Single Next.js full-stack app (API routes + Prisma)** — would have meant
  porting the domain calculations to TypeScript and losing the Python
  pipeline ecosystem; the split also demonstrates a typed cross-language
  contract, which is part of the portfolio's point.

## Consequences

- Three moving parts instead of one; `docker compose up --build` is the
  supported way to run the full stack, and a `Makefile` covers the common
  workflows.
- The OpenAPI snapshot must be regenerated when the API changes (enforced by
  CI drift checks rather than left to discipline).
- Frontend testing is deliberately thinner than backend testing in Phase 1
  (build gate only) — see `docs/phase-2-roadmap.md`.
