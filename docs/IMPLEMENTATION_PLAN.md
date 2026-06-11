# Implementation Plan

## Phase 1 — Core Backend (Complete)

**Goal:** Website chat → FastAPI → Rule-based classification → PostgreSQL → Safe reply → Human handover

### Milestone 1.1 — Project Skeleton
- [x] Git repository with correct remote
- [x] CLAUDE.md, AGENTS.md, .gitignore, .env.example
- [x] backend/pyproject.toml with all dependencies
- [x] backend/Dockerfile
- [x] docker-compose.yml (backend + PostgreSQL)
- [x] Makefile

### Milestone 1.2 — Application Foundation
- [x] Pydantic Settings config (app/config.py)
- [x] Structured logging (app/logging_config.py)
- [x] Async SQLAlchemy engine + session factory (app/database/)
- [x] Alembic configuration + initial migration

### Milestone 1.3 — Data Layer
- [x] Contact model
- [x] PlatformAccount model
- [x] Conversation model
- [x] Message model
- [x] LeadEvaluation model
- [x] HandoffEvent model
- [x] All repositories (CRUD operations)

### Milestone 1.4 — Business Logic
- [x] Deterministic LeadClassifier (rule-based, no AI API)
- [x] ReplyGenerator (safe templates per temperature)
- [x] ChatService (orchestrates the full pipeline)

### Milestone 1.5 — API Layer
- [x] GET / (root)
- [x] GET /health/live
- [x] GET /health/ready
- [x] POST /api/v1/chat/messages
- [x] GET /api/v1/conversations/{id}
- [x] GET /api/v1/conversations/{id}/messages
- [x] POST /api/v1/conversations/{id}/handoff
- [x] POST /api/v1/conversations/{id}/resume-ai

### Milestone 1.6 — Tests
- [x] Health endpoint tests
- [x] Classifier unit tests (hot/warm/cold/not-lead/handoff triggers)
- [x] Chat API integration tests (persistence, dedup, blank message, invalid email)
- [x] AI-disabled-after-handover test
- [x] Resume-AI test

### Milestone 1.7 — Documentation
- [x] README.md
- [x] docs/REQUIREMENTS.md
- [x] docs/IMPLEMENTATION_PLAN.md
- [x] docs/IMPLEMENTATION_STATUS.md
- [x] MANUAL_ACTIONS.md

---

## Phase 2 — AI Enhancement (Planned)

- Replace rule-based classifier with OpenAI GPT-4o-mini
- n8n webhook for sales team notification
- Admin API endpoints

## Phase 3 — Social Platforms (Planned)

- Facebook Messenger webhook
- Instagram DM + comment-to-DM

## Phase 4 — LinkedIn (Planned)

- LinkedIn OAuth + message API

## Phase 5 — Production (Planned)

- Cloud deployment
- Monitoring and alerting
- Rate limiting and abuse prevention
