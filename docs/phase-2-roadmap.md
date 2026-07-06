# Phase 2 Roadmap

Everything in this file was **consciously deferred** during the Phase 1
rebuild, not forgotten. Nothing here is stubbed or half-built in the code —
if a feature is listed below, it does not exist yet, and the application does
not pretend otherwise. Items are grouped by theme, not priority.

## Data

- **Live Destatis / Bundesagentur für Arbeit / BBSR integration.** Phase 1
  ships a hand-compiled reference snapshot
  (`data/reference/cities_reference_2023.csv`, see
  [`data-provenance.md`](data-provenance.md)). The pipeline's extract stage is
  an adapter interface precisely so that a real HTTP adapter against a
  license-verified government source can replace the local CSV without
  touching the validate/normalize/transform/load/publish stages.
- **Offline postal-code dataset fallback.** Postal-code lookup calls the free
  [zippopotam.us](https://api.zippopotam.us) API and degrades gracefully when
  it is unreachable, but no static PLZ dataset is bundled as a fallback yet.
- **Verification of the gross-to-net estimate against authoritative sources.**
  The optional net-income estimate uses versioned, clearly labeled
  assumptions (`NET_INCOME_ASSUMPTIONS_2026`). The contribution rates should
  be verified against BMF / Sozialversicherungsentgeltverordnung publications
  before anyone treats the output as more than an illustrative estimate.

## Security hardening

Baseline security is **built and tested** in Phase 1 (Argon2id password
hashing, HttpOnly `SameSite=Lax` session cookies with real server-side
revocation, per-query ownership enforcement with cross-user isolation tests,
Pydantic validation on every request body). Deferred on top of that baseline:

- CSRF double-submit tokens (the `SameSite=Lax` cookie is the current CSRF
  mitigation; a token adds defense in depth).
- Rate limiting on auth and demo-provisioning endpoints.
- Security-header middleware (CSP, HSTS, `X-Content-Type-Options`, …).
- An audit-log table for sensitive account events.
- `PRIVACY.md`, `SECURITY.md`, a written threat model, and a data-flow
  diagram.
- Dependency- and secret-scanning CI jobs (Dependabot version updates are
  already configured in `.github/dependabot.yml`; scanning workflows are not).

## Testing

Phase 1 testing is deliberately backend-first: the financial logic and every
API behavior are covered by pytest, while frontend CI is a lint + typecheck +
build gate only. Deferred:

- Playwright end-to-end suite (login, CRUD, CSV round-trip, isolation).
- Vitest component tests for the chart wrappers and forms.
- Automated accessibility audits (axe or equivalent) wired into CI.

## Product

- **External AI insight abstraction.** The insights engine is 100 %
  deterministic rules by design; Phase 1 contains no AI code at all. A future
  phase could add an optional LLM-backed explanation layer *behind* the same
  `Insight` schema, so the deterministic rules remain the source of truth.
- **Multi-member households.** The data model is single-user-per-household;
  shared households with roles/invitations are not modeled.
- **Weekly-recurrence proration.** Recurring entries currently count once per
  month in monthly aggregations regardless of frequency — a documented
  simplification (see the docstring in
  `apps/api/app/repositories/finance.py`). Correct proration (×4.33 for
  weekly, ÷3 for quarterly, …) belongs with a recurrence-aware aggregation
  pass.
- **Password-reset email delivery.** The reset-token flow works end to end,
  but no transactional email service is wired up; in development the token is
  only logged server-side.
- **Draggable dashboard widgets.** The overview layout is fixed.
- **English UI content.** The i18n plumbing (next-intl) is in place and all
  strings live in `apps/web/src/messages/de.json`, but no `en.json` is
  shipped — German only, rather than a half-checked machine translation.
