# Architecture Overview

Three deployable units — a Next.js frontend, a FastAPI backend, and
PostgreSQL — plus a framework-free Python domain package, organized as a
monorepo:

```
apps/
  web/          Next.js 16 (App Router), TypeScript strict, Tailwind v4,
                Radix primitives, TanStack Query, next-intl (German)
  api/          FastAPI, SQLAlchemy 2 (async), Alembic, fastapi-users,
                APScheduler, pytest
packages/
  analytics/    pure-Python domain calculations + deterministic insights
                engine — no FastAPI/SQLAlchemy imports, tested in isolation
  shared/       OpenAPI schema snapshot + TypeScript types generated from it
data/
  reference/    hand-compiled city reference snapshot (see data-provenance.md)
  seeds/        default category definitions
infrastructure/docker/  api.Dockerfile, web.Dockerfile, entrypoint
docker-compose.yml      postgres + api + web
```

## Backend layering

```
Routers  →  Services  →  Repositories  →  Models
(HTTP only)  (orchestration; the      (the only layer     (SQLAlchemy)
              only layer that          touching SQLAlchemy
              imports analytics)       queries; owns
                                       ownership enforcement)
```

- **Routers** (`apps/api/app/routers/`): auth, account, demo, categories,
  income, expenses, budgets, savings_goals, cities, data, insights. HTTP
  concerns only — request/response schemas, status codes, dependencies.
- **Services** orchestrate use cases and are the only backend layer that
  imports `packages/analytics`, so domain math has exactly one entry point.
- **Repositories** are the only layer executing queries. Everything
  user-owned extends `UserOwnedRepository`
  (`apps/api/app/repositories/base.py`), which structurally forces every
  query through a `.where(user_id == ...)` filter with the id sourced from
  the authenticated session — never from request parameters. Cross-user
  access yields 404 and is proven by a parametrized isolation test across
  every entity type (`tests/integration/test_ownership_isolation.py`).
- **`packages/analytics`** sits outside the stack entirely: plain-Python
  functions and dataclasses for net-income estimation, disposable income,
  rent burden, savings projection, recurrence expansion, and the ten insight
  rules. This separation is what makes "the financial math is tested" a
  checkable claim — its 88 tests run with no database and no HTTP.

## Why a rebuild, not a refactor

The Streamlit prototype's problems were structural (business logic duplicated
between chart helpers and calculator, live HTML scraping as the primary data
path, a data-year inconsistency between SQL and UI, no auth/tests/migrations)
— documented in [`initial-audit.md`](../initial-audit.md). Decision records
for the major choices live in [`decisions/`](decisions/):

- [ADR-0001](decisions/0001-nextjs-fastapi-postgres-stack.md) — stack choice
- [ADR-0002](decisions/0002-fastapi-users-for-auth.md) — auth library
- [ADR-0003](decisions/0003-reference-dataset-instead-of-scraping.md) — reference data instead of scraping

## Authentication, sessions, demo mode

fastapi-users with Argon2id hashing (pinned explicitly, not left to library
default) and a **database-backed session strategy**: the session cookie
(HttpOnly, `SameSite=Lax`, `Secure` in production) references an
`access_tokens` row, so logout genuinely revokes the session server-side —
no JWT denylist or Redis needed. Password reset uses the built-in token flow;
no email delivery is wired up in Phase 1 (token logged server-side, see
[`../phase-2-roadmap.md`](../phase-2-roadmap.md)).

Demo mode creates a *real* user row (`is_demo=true`, no credentials), seeds
example data, and issues the same session cookie as a normal login — the
rest of the app has no demo-specific code path. An APScheduler job inside
the FastAPI lifespan deletes expired demo users hourly (cascading via FKs);
`make demo-reset` forces expiry immediately.

One route-ordering constraint worth knowing: `DELETE /users/me` must be
registered *before* the fastapi-users users router, or the library's
catch-all `/users/{id}` route shadows it.

## Data pipeline

`apps/api/app/pipeline/` implements extract → validate → normalize →
transform → load → publish over the reference CSV, with tenacity
retry/backoff at extract (the adapter interface is designed for a future HTTP
source), IQR/z-score outlier detection recorded as `validation_results` rows
(never silently clipped), and a staged-publish pointer: snapshots become
visible only when `import_runs.published_at` is set, which is refused while
error-severity validation findings exist. Consumers always read the latest
*published* run — the class of bug where two code paths disagree about the
data year is structurally impossible. CLI:
`python -m app.pipeline.cli refresh|validate|status` (wrapped by
`make data-refresh|data-validate|data-status`).

## Insights engine

Ten deterministic rules in `packages/analytics/analytics/insights/rules/`
(budget overrun, spending increase vs. trailing average, duplicate recurring
expenses, category-share change, missing categories, savings-goal delay, high
rent burden, negative cash flow, outdated reference data, missing inputs),
each returning typed `Insight` objects with severity, evidence, estimated
savings range, assumptions, and a disclaimer. The engine isolates per-rule
exceptions so one failing rule cannot break the endpoint. All evaluations
remain deterministic, inspectable, and reproducible.

## Frontend

App Router with two route groups: `(auth)` (login, register,
forgot/reset-password) and `(dashboard)` (overview, income, expenses,
categories, budgets incl. savings goals, city comparison, data sources,
settings, privacy). Server state lives in TanStack Query keyed to the API;
the selected month lives in the URL (`?month=2026-06`), not a client store.
Charts are thin Recharts wrappers with all colors mapped from a single theme
token module. Session-changing transitions (login/logout) navigate via
`window.location.assign` rather than the client router, because Next.js
prefetching can cache the auth proxy's redirect responses. Note: Next.js 16
renamed `middleware.ts` to `proxy.ts` — the auth gate lives in
`apps/web/src/proxy.ts`.

## API contract

The FastAPI OpenAPI schema is exported to
`packages/shared/openapi/openapi.json`
(`apps/api/scripts/export_openapi.py`) and `openapi-typescript` generates
`packages/shared/src/types.ts` from it. CI checks both directions for drift:
the backend workflow re-exports the schema and the frontend workflow
regenerates the types, each failing if the committed artifact is stale.

## Deployment

`docker compose up --build` starts postgres → api → web. The API entrypoint
runs `alembic upgrade head` on start (migration 0003 seeds default
categories); reference data is loaded explicitly with `make seed`. Both
images run as non-root users with container healthchecks. Configuration is
environment-only (`.env`, see `.env.example`); `SESSION_SECRET` has no
default and compose refuses to start without it.
