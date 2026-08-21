# syntax=docker/dockerfile:1

FROM node:22-alpine AS web-build

WORKDIR /build/web

COPY web/package*.json ./
# 与 app-ci.yml 主机侧同源加固：node:22-alpine 自带的 npm 10.9.x 被指认为
# "Exit handler never called!" 的来源，先固定到 npm 11，再限制 fetch 超时，
# 让注册表挂起在 60 秒内快速失败；每次重试前清理缓存与半成品 node_modules。
RUN set -eu; \
    npm install -g npm@11 --no-audit --no-fund --no-progress; \
    export npm_config_fetch_timeout=60000 \
           npm_config_fetch_retries=3 \
           npm_config_fetch_retry_mintimeout=2000 \
           npm_config_fetch_retry_maxtimeout=20000; \
    if [ -f package-lock.json ]; then install_cmd="npm ci"; else install_cmd="npm install"; fi; \
    for attempt in 1 2 3; do \
      echo "web deps: ${install_cmd} (attempt ${attempt}/3)"; \
      if ${install_cmd} --no-audit --no-fund --no-progress; then \
        exit 0; \
      fi; \
      npm cache clean --force || true; \
      rm -rf node_modules; \
      sleep $((attempt * 10)); \
    done; \
    echo "web deps: falling back to a fresh resolution without the lockfile"; \
    npm install --no-package-lock --no-audit --no-fund --no-progress

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
