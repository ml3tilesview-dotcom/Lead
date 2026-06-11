from pydantic import BaseModel, Field


class LeadEvaluationSchema(BaseModel):
    is_lead: bool
    lead_temperature: str  # hot / warm / cold / not_lead
    intent: str
    lead_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    product_interest: str | None = None
    conversation_summary: str | None = None
    handoff_required: bool
    handoff_reason: str | None = None
