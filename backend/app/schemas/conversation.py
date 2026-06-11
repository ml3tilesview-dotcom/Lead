import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    id: uuid.UUID
    direction: str
    sender_type: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: uuid.UUID
    platform: str
    status: str
    ai_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationMessagesResponse(BaseModel):
    conversation_id: uuid.UUID
    messages: list[MessageSchema]
    total: int
