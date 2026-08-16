# syntax=docker/dockerfile:1

FROM node:22-alpine AS web-build

WORKDIR /build/web

COPY web/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install --no-audit --no-fund; fi

COPY web/ ./
COPY packages/ /build/packages/
RUN npm run build


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/api/src:/app/worker/src \
    SCUT_SENIOR_APP_ROOT=/app \
    SCUT_SENIOR_STATIC_DIR=/app/static \
    SCUT_SENIOR_DATABASE_PATH=/app/.local/iteration-zero.db

WORKDIR /app

RUN groupadd --system --gid 10001 scut-senior \
    && useradd --system --uid 10001 --gid scut-senior --home-dir /app scut-senior

COPY worker/ ./worker/
COPY api/ ./api/
RUN python -m pip install ./worker ./api

# Iteration 0 reads public contracts and deterministic fixtures at runtime.
# They are small application inputs, not the real knowledge corpus.
COPY packages/ ./packages/
COPY tests/fixtures/ ./tests/fixtures/
COPY --from=web-build /build/web/dist/ ./static/

RUN mkdir -p /app/.local /app/web \
    && ln -s /app/static /app/web/dist \
    && chown -R scut-senior:scut-senior /app/.local /app/static /app/web

USER scut-senior

EXPOSE 8000

CMD ["uvicorn", "scut_senior_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
