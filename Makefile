.PHONY: help up down build logs migrate seed demo-reset \
	api-install api-dev api-test api-lint api-typecheck \
	web-install web-dev web-build web-lint web-typecheck \
	test lint data-refresh data-validate data-status

help:
	@echo "Docker workflow:"
	@echo "  make up              Start web+api+postgres (docker compose up --build)"
	@echo "  make down            Stop and remove containers"
	@echo "  make migrate         Run Alembic migrations inside the api container"
	@echo "  make seed            Seed default categories and demo reference data"
	@echo "  make demo-reset      Force-expire and delete all demo accounts now"
	@echo ""
	@echo "Fast local workflow (no Docker, requires local Postgres + Python 3.12 + Node 20+):"
	@echo "  make api-install     Install backend + analytics package in editable mode"
	@echo "  make api-dev         Run FastAPI with autoreload"
	@echo "  make web-install     Install frontend dependencies"
	@echo "  make web-dev         Run the Next.js dev server"
	@echo ""
	@echo "Quality gates:"
	@echo "  make test            Run backend + analytics test suites"
	@echo "  make lint             Run backend and frontend linters"
	@echo ""
	@echo "Data pipeline:"
	@echo "  make data-refresh    Run the full extract-to-publish pipeline"
	@echo "  make data-validate   Dry run: extract + validate only, no load/publish"
	@echo "  make data-status     Show the latest import run per data source"

# --- Docker workflow ---

up:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m app.pipeline.cli refresh
	docker compose exec api python scripts/seed_categories.py

demo-reset:
	docker compose exec api python scripts/demo_reset.py

# --- Fast local workflow ---

api-install:
	pip install -e packages/analytics
	pip install -e apps/api[dev]

api-dev:
	cd apps/api && uvicorn app.main:app --reload --port 8000

api-test:
	pytest packages/analytics/tests apps/api/tests

api-lint:
	ruff check packages/analytics apps/api
	ruff format --check packages/analytics apps/api

api-typecheck:
	mypy packages/analytics/analytics apps/api/app

web-install:
	npm install --prefix apps/web

web-dev:
	npm run dev --prefix apps/web

web-build:
	npm run build --prefix apps/web

web-lint:
	npm run lint --prefix apps/web

web-typecheck:
	npm run typecheck --prefix apps/web

# --- Quality gates ---

test: api-test

lint: api-lint web-lint

# --- Data pipeline ---

data-refresh:
	cd apps/api && python -m app.pipeline.cli refresh

data-validate:
	cd apps/api && python -m app.pipeline.cli validate

data-status:
	cd apps/api && python -m app.pipeline.cli status
