import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead_evaluation import LeadEvaluation
from app.schemas.lead import LeadEvaluationSchema


class LeadEvaluationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
        evaluation: LeadEvaluationSchema,
    ) -> LeadEvaluation:
        record = LeadEvaluation(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            message_id=message_id,
            is_lead=evaluation.is_lead,
            lead_temperature=evaluation.lead_temperature,
            intent=evaluation.intent,
            lead_score=evaluation.lead_score,
            confidence=evaluation.confidence,
            reason=evaluation.reason,
            product_interest=evaluation.product_interest,
            conversation_summary=evaluation.conversation_summary,
            handoff_required=evaluation.handoff_required,
            handoff_reason=evaluation.handoff_reason,
        )
        self.db.add(record)
        await self.db.flush()
        return record
