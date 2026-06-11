# AI Lead Generation and Social Media Auto-Reply System

A production-oriented backend prototype for capturing, classifying, and responding to customer messages for a SaaS company (e.g. TilesView / TilesWale).

## Phase 1 Features

- Receive customer messages via REST API (website chat)
- Deterministic rule-based lead classification: Hot / Warm / Cold / Not Lead
- Safe template replies — no invented pricing or guarantees
- Automatic handoff to sales team for hot leads
- Full conversation and lead history stored in PostgreSQL
- Duplicate message detection
- AI reply disabled after human handoff, resumable via API
- Docker Compose for local development
- Full test suite (no paid APIs required)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11+ |
| API Framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x (async) |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| HTTP Client | HTTPX |
| Testing | pytest + pytest-asyncio |
| Linter | Ruff |
| Containers | Docker + Docker Compose |

## Architecture

```
POST /api/v1/chat/messages
         │
         ▼
   ChatService
    ├── ContactRepository      → upsert contact
    ├── ConversationRepository → get or create conversation
    ├── MessageRepository      → save inbound, check dedup
    ├── LeadClassifier         → rule-based scoring
    ├── ReplyGenerator         → safe template reply
    ├── LeadEvaluationRepo     → persist evaluation
    ├── MessageRepository      → save outbound reply
    └── HandoffEventRepository → create handoff if required
```

## Folder Structure

```
lead/
├── CLAUDE.md               Persistent instructions for Claude Code
├── AGENTS.md               Instructions for other AI coding agents
├── README.md               This file
├── MANUAL_ACTIONS.md       Tasks requiring human action
├── .env.example            Environment variable template
├── .gitignore
├── docker-compose.yml
├── Makefile
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/0001_initial_schema.py
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── api/          (health, chat, conversations)
│   │   ├── database/     (engine, session, base)
│   │   ├── models/       (SQLAlchemy ORM)
│   │   ├── repositories/ (database operations)
│   │   ├── schemas/      (Pydantic v2)
│   │   └── services/     (classifier, reply, chat)
│   └── tests/
└── docs/
    ├── REQUIREMENTS.md
    ├── IMPLEMENTATION_PLAN.md
    └── IMPLEMENTATION_STATUS.md
```

## Windows Setup

```powershell
# 1. Install Docker Desktop (https://www.docker.com/products/docker-desktop/)
# 2. Install Python 3.11+ (https://python.org)
# 3. Clone the repository
git clone https://github.com/ml3tilesview-dotcom/Lead.git
cd Lead
```

## Environment Setup

```powershell
copy .env.example .env
# Edit .env — for local Docker use, defaults work out of the box
```

## Docker Setup (Recommended)

```powershell
docker compose up --build
# Backend: http://localhost:8000
# Docs:    http://localhost:8000/docs
```

## Python Local Setup (Without Docker)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Database Migration

```powershell
# With Docker running:
docker compose exec backend alembic upgrade head

# Locally (requires PostgreSQL):
cd backend
$env:DATABASE_URL="postgresql+asyncpg://lead_user:lead_pass@localhost:5432/lead_db"
alembic upgrade head
```

## Running the Backend

```powershell
# Docker (recommended):
docker compose up

# Local:
cd backend
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```powershell
cd backend
pytest -v
```

Tests use SQLite in-memory — no PostgreSQL or external API keys required.

## Example Request

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "visitor-001",
    "external_message_id": "msg-001",
    "name": "John Smith",
    "email": "john@example.com",
    "message": "I would like to book a demo of your tile viewer",
    "platform": "website"
  }'
```

## Example Response

```json
{
  "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "incoming_message_id": "...",
  "outgoing_message_id": "...",
  "duplicate": false,
  "processing_status": "processed",
  "lead_evaluation": {
    "is_lead": true,
    "lead_temperature": "hot",
    "intent": "demo_request",
    "lead_score": 85,
    "confidence": 0.6,
    "reason": "Hot signals: demo_request",
    "product_interest": null,
    "conversation_summary": "User message: I would like to book a demo...",
    "handoff_required": true,
    "handoff_reason": "Mandatory handoff triggered by: demo_request"
  },
  "reply": "Hi John,\n\nThank you for your interest in a demo! Our sales team will be in touch...",
  "handoff_required": true,
  "conversation_status": "handed_off"
}
```

## Current Limitations

- Phase 1 classifier is rule-based — complex or ambiguous messages may be misclassified
- No authentication on the chat endpoint
- No rate limiting
- Handoff notifications are DB-only — no webhook delivery yet
- No frontend chat widget — API only

## Next Phases

| Phase | Feature |
|-------|---------|
| Phase 2 | OpenAI GPT-4o-mini classifier, n8n webhook, admin UI |
| Phase 3 | Facebook Messenger, Instagram DM + comment-to-DM |
| Phase 4 | LinkedIn integration |
| Phase 5 | Production deployment, monitoring, rate limiting |
