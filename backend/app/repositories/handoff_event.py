import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.handoff_event import HandoffEvent


class HandoffEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        conversation_id: uuid.UUID,
        reason: str,
        handoff_type: str = "sales",
        notes: str | None = None,
    ) -> HandoffEvent:
        event = HandoffEvent(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            reason=reason,
            handoff_type=handoff_type,
            status="pending",
            notes=notes,
        )
        self.db.add(event)
        await self.db.flush()
        return event
