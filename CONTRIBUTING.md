# Contributing

This is primarily a personal portfolio project, but it is structured to be
readable and extendable by others.

## Local setup

See the "Local setup" and "Docker setup" sections of the [README](README.md).
The short version:

```bash
docker compose up --build
```

For the faster non-Docker workflow, see `make help`.

## Coding style

- Python: [Ruff](https://docs.astral.sh/ruff/) for linting and formatting,
  type hints checked with mypy. Run `make api-lint api-typecheck`.
- TypeScript: ESLint + `tsc --noEmit` under strict mode. Run
  `make web-lint web-typecheck`.
- Keep domain calculations in `packages/analytics` free of FastAPI/SQLAlchemy
  imports — they should stay independently unit-testable.

## Adding a database migration

```bash
cd apps/api
alembic revision --autogenerate -m "short description"
```

Review the generated migration before committing — autogenerate does not
always infer intent correctly (renames, check constraints).

## Adding a new insight rule

1. Add a module under `packages/analytics/analytics/insights/rules/`
   returning zero or more `Insight` objects from a pure function.
2. Register it in `packages/analytics/analytics/insights/engine.py`.
3. Add a test under `packages/analytics/tests/insights/` covering both the
   "fires" and "does not fire" boundary.

## Pull request checklist

- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] `make api-typecheck` / `make web-typecheck` pass
- [ ] New behavior has a corresponding test
- [ ] No secrets, `.env` files, or TODO markers were committed
