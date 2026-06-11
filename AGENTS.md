# AGENTS.md — Repository Instructions for Coding Agents

This file provides instructions for any AI coding agent (Codex, Copilot Workspace,
Devin, etc.) working in this repository.

## Mandatory Rules

1. **Inspect first.** Read existing files before editing. Never overwrite working code
   without understanding what it does.
2. **Stay in scope.** Only read and modify files inside this repository.
3. **No real credentials.** Never write API keys, passwords, or tokens into any file.
   Use environment variables. Reference `.env.example` for variable names.
4. **`.env` is private.** It is git-ignored. Never commit it.
5. **Type everything.** All Python functions, methods, and class attributes must have
   type annotations.
6. **Small handlers.** Route handlers validate input and delegate to services.
   Services contain business logic. Repositories contain database access.
7. **Explicit errors.** Do not swallow exceptions silently. Log or re-raise.
8. **Real tests only.** Run `pytest` and report actual results. Do not fabricate output.
9. **No paid APIs in tests.** Tests must pass without OpenAI, Meta, or any paid service.
10. **Document changes.** Update `docs/IMPLEMENTATION_STATUS.md` after each phase.
11. **External work log.** Add an entry to `MANUAL_ACTIONS.md` for anything that
    requires the repository owner to act outside the codebase.
12. **Git safety.** Never force-push. Never rebase published commits.

## Project Layout

```
backend/app/
  api/        — FastAPI routers (thin handlers only)
  services/   — Business logic (classification, reply generation, handoff)
  repositories/ — Database CRUD operations (SQLAlchemy)
  models/     — SQLAlchemy ORM models
  schemas/    — Pydantic v2 request/response schemas
  database/   — Engine, session factory, base
```

## Current Phase

Phase 1 — Website chat → FastAPI → Rule-based classification → PostgreSQL → Safe reply.
No external AI API, no social platform integration.

## Running Locally

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

## Running Tests

```bash
cd backend
pytest -v
```
