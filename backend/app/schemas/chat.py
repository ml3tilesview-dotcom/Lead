import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from .lead import LeadEvaluationSchema


class ChatMessageRequest(BaseModel):
    external_user_id: str = Field(..., min_length=1, max_length=255)
    external_message_id: str = Field(..., min_length=1, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company_name: str | None = Field(default=None, max_length=255)
    message: str = Field(..., min_length=1, max_length=4000)
    platform: Literal["website", "facebook", "instagram", "linkedin"] = "website"

    @field_validator("message", mode="before")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if isinstance(v, str) and not v.strip():
            raise ValueError("Message must not be blank")
        return v


class ChatMessageResponse(BaseModel):
    conversation_id: uuid.UUID
    incoming_message_id: uuid.UUID
    outgoing_message_id: uuid.UUID
    duplicate: bool
    processing_status: str
    lead_evaluation: LeadEvaluationSchema
    reply: str
    handoff_required: bool
    conversation_status: str
