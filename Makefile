.PHONY: help install lint format test migrate up down logs clean

help:
	@echo "Available targets:"
	@echo "  install   Install Python dependencies"
	@echo "  lint      Run ruff linter"
	@echo "  format    Run ruff formatter"
	@echo "  test      Run pytest"
	@echo "  migrate   Run Alembic migrations"
	@echo "  up        Start Docker Compose services"
	@echo "  down      Stop Docker Compose services"
	@echo "  logs      Tail backend logs"
	@echo "  clean     Remove __pycache__ and .pytest_cache"

install:
	cd backend && pip install -e ".[dev]"

lint:
	cd backend && ruff check app tests

format:
	cd backend && ruff format app tests

test:
	cd backend && pytest -v

migrate:
	cd backend && alembic upgrade head

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f backend

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
