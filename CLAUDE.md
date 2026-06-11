# CLAUDE.md — Persistent Instructions for Claude Code

This file is read by Claude Code at the start of every session in this repository.
Follow all instructions below without exception.

## Repository Rules

- Inspect all existing files before making any edits.
- Work only inside this repository. Never read or modify files outside the workspace.
- Never add real credentials, API keys, passwords or secrets to any file.
- Always use environment variables for configuration.
- Never commit `.env`. The `.env` file is git-ignored by design.
- `.env.example` contains only placeholder values and IS committed.

## Code Quality

- Use typed, modular and maintainable Python throughout.
- Keep route handlers small — only validate input and call services.
- Put business logic in service classes under `backend/app/services/`.
- Put database operations in repository classes under `backend/app/repositories/`.
- Do not silently catch errors. Let exceptions propagate or log them explicitly.
- All models, schemas and service methods must use Python type annotations.

## Testing

- Run `pytest` before claiming any feature is complete.
- Do not fabricate test results. Show actual output.
- Tests must not call paid external services (OpenAI, Meta APIs, etc.).
- Use an in-memory SQLite database for unit tests where PostgreSQL is unavailable.

## Documentation

- Update `docs/IMPLEMENTATION_STATUS.md` after completing each phase.
- Update `README.md` whenever project setup steps or API behavior changes.
- Record any task that requires external accounts or credentials in `MANUAL_ACTIONS.md`.

## Git

- Do not force-push.
- Do not alter Git history.
- Do not push unless authentication is available and validation passes.
- Use `.gitignore` to exclude `.env`, `__pycache__`, `.venv`, build artifacts.

## Docker

- `docker-compose.yml` must work with `docker compose up --build`.
- Include health checks for both PostgreSQL and backend services.
- Never bake real credentials into Docker images.

## Phase Discipline

- Complete the current phase fully before beginning the next.
- After each phase: run linter, run tests, update `docs/IMPLEMENTATION_STATUS.md`.
