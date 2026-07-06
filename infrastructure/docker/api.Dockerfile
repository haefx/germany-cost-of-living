# Build context is the repository root (see docker-compose.yml), because the
# API depends on the local packages/analytics package as an editable install.

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY packages/analytics ./packages/analytics
COPY apps/api ./apps/api
COPY data ./data

RUN pip install -e ./packages/analytics && \
    pip install -e ./apps/api

RUN useradd --create-home --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

WORKDIR /app/apps/api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

COPY --chown=appuser:appuser infrastructure/docker/api-entrypoint.sh /app/api-entrypoint.sh
ENTRYPOINT ["sh", "/app/api-entrypoint.sh"]
