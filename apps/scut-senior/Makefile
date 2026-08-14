.PHONY: sync dev-api test test-api test-web build-web validate-fixtures check-contracts

sync:
	uv sync --project api --extra dev
	npm --prefix web ci

dev-api:
	uv run --project api uvicorn scut_senior_api.main:app --reload --host 127.0.0.1 --port 8000

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
