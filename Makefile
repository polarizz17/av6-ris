.PHONY: venv install install-dev lint typecheck fmt pre-commit-install docker-build docker-up docker-down docker-logs
venv: ; python3 -m venv .venv
install: ; . .venv/bin/activate && pip install -r requirements.txt
install-dev: ; . .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
lint: ; ruff check .
typecheck: ; mypy .
fmt: ; black . && ruff check --fix .
pre-commit-install: ; . .venv/bin/activate && pre-commit install && pre-commit autoupdate
docker-build: ; docker build -t ris-watcher:latest .
docker-up: ; docker compose up -d --build
docker-down: ; docker compose down
docker-logs: ; docker compose logs -f
