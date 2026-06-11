import uuid
from datetime import datetime

from pydantic import BaseModel


class HandoffRequest(BaseModel):
    reason: str
    handoff_type: str = "sales"
    notes: str | None = None


class HandoffResponse(BaseModel):
    handoff_event_id: uuid.UUID
    conversation_id: uuid.UUID
    status: str
    reason: str
    created_at: datetime
