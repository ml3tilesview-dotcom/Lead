# Requirements

## Functional Requirements

### Phase 1 (Implemented)

- FR-01: Accept customer messages via REST API (website chat)
- FR-02: Validate and sanitize all incoming message data
- FR-03: Reject blank or oversized messages
- FR-04: Identify and reject duplicate external message IDs
- FR-05: Create or update contact records from message metadata
- FR-06: Create or continue conversations per contact per platform
- FR-07: Classify messages as Hot / Warm / Cold / Not Lead using deterministic rules
- FR-08: Generate safe, template-based replies appropriate to lead temperature
- FR-09: Store all messages, evaluations, and replies in PostgreSQL
- FR-10: Create handoff events for hot leads (demo, pricing, purchase intent, human request)
- FR-11: Disable AI replies for conversations after human handoff
- FR-12: Allow resumption of AI replies via API endpoint
- FR-13: Expose conversation history via API
- FR-14: Expose liveness and readiness health checks

### Phase 2 (Planned)

- FR-20: Replace rule-based classifier with OpenAI GPT-4o-mini
- FR-21: Notify sales team via n8n webhook on hot-lead handoff
- FR-22: Admin dashboard for lead review

### Phase 3 (Planned)

- FR-30: Facebook Messenger webhook integration
- FR-31: Instagram DM webhook integration
- FR-32: Instagram comment-to-DM conversion
- FR-33: Platform message normalisation layer

### Phase 4 (Planned)

- FR-40: LinkedIn message integration

## Non-Functional Requirements

- NFR-01: All endpoints must respond within 2 seconds under normal load
- NFR-02: No real credentials committed to version control
- NFR-03: Tests must pass without paid external services
- NFR-04: Application must work with Docker Compose for local development
- NFR-05: All Python code must pass Ruff linting
- NFR-06: UUID primary keys on all tables
- NFR-07: Idempotent message processing (duplicate handling)
