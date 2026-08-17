.PHONY: sync dev-api serve-online test test-api test-web build-web validate-fixtures check-contracts

sync:
	uv sync --project api --extra dev
	npm --prefix web ci

dev-api:
	uv run --project api uvicorn scut_senior_api.main:app --reload --host 127.0.0.1 --port 8000

# 在线部署（本地 + HTTPS 隧道，当前启用路径）：先 make build-web，
# 再按 README「在线部署」节设置环境变量后执行；前端与 API 由同一进程提供。
serve-online:
	uv run --project api uvicorn scut_senior_api.main:app --host 0.0.0.0 --port 8000

test: test-api test-web

test-api:
	uv run --project api pytest tests/python

test-web:
	npm --prefix web run test
	npm --prefix web run typecheck

build-web:
	npm --prefix web run build

validate-fixtures:
	uv run --project api scut-senior-corpus-validate \
		--manifest tests/fixtures/corpus/manifest.csv \
		--knowledge-root tests/fixtures/corpus \
		--pretty

check-contracts:
	uv run --project api python -m scut_senior_api.export_contracts --check
