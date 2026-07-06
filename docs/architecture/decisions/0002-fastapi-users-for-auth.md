# ADR-0002: fastapi-users with a database session strategy

- **Status**: accepted (2026-07)
- **Context**: authentication for the Phase 1 rebuild

## Context

The app needs boring, correct email/password authentication: registration,
login, logout that actually revokes the session, password reset, and a demo
mode that issues the same kind of session as a real login. No OAuth/social
login is required in Phase 1.

## Decision

Use **fastapi-users** with:

- **Argon2id** password hashing, pinned explicitly via its password-helper
  configuration rather than relying on library defaults.
- **Cookie transport**: HttpOnly, `SameSite=Lax`, `Secure` in production —
  no tokens in `localStorage`, and `Lax` is the Phase 1 CSRF mitigation
  (a double-submit token is on the Phase 2 roadmap).
- **`DatabaseStrategy` over an `access_tokens` table** instead of JWTs:
  logout deletes the row, so revocation is immediate and server-side, with no
  denylist or Redis. Session lookups cost one indexed query — acceptable at
  this scale and simpler than distributed token invalidation.
- The built-in password-reset token flow, without email delivery in Phase 1
  (token is logged server-side; documented limitation).

## The maintenance-mode caveat

At decision time, fastapi-users had announced **maintenance mode**: security
and dependency updates continue, but no new features, while a successor
toolkit is developed. We checked this explicitly and chose it anyway,
because:

1. The feature set we need is complete and stable; we need no new features
   from the library.
2. Security updates — the part that matters — continue.
3. Our integration surface is small and standard (SQLAlchemy adapter, cookie
   transport, database strategy), which keeps a future migration contained.

**Documented fallback**: if fastapi-users becomes a liability (e.g., blocks a
FastAPI/SQLAlchemy upgrade), the replacement is a ~150-line hand-rolled
module — argon2-cffi for hashing plus an opaque random token stored in the
same `access_tokens` table, verified by a FastAPI dependency. The
`UserOwnedRepository` ownership layer and all route contracts are independent
of the auth library, so the swap would not ripple through the codebase.

## Alternatives considered

- **Hand-rolled auth from the start** — rejected for Phase 1: the library's
  battle-tested request handling (timing-safe verification, token lifecycle,
  hashing configuration) is worth more than independence, and the fallback
  path keeps us un-trapped.
- **JWT sessions** — rejected: stateless tokens make immediate logout/
  revocation impossible without adding a denylist store, which erases the
  supposed simplicity win.
- **External IdP (Auth0/Keycloak/…)** — overkill for a portfolio app meant
  to run from a single `docker compose up`, and it would outsource exactly
  the part meant to be demonstrated.

## Consequences

- Logout, account deletion, and demo expiry all revoke sessions by deleting
  rows — one consistent mechanism, covered by integration tests.
- One route-ordering gotcha to preserve: custom `/users/me` routes must be
  registered before the fastapi-users users router, whose `/users/{id}`
  pattern otherwise shadows them (regression-tested).
- The library pin should be revisited when the successor toolkit ships; the
  fallback above is the exit strategy either way.
