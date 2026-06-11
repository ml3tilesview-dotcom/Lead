import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_with_messages(self, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_active_for_contact(
        self, contact_id: uuid.UUID, platform: str
    ) -> Conversation | None:
        # Return any open conversation (active or handed_off) — do NOT create a new one
        # after handoff, new messages from the same user continue the same conversation.
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.contact_id == contact_id,
                Conversation.platform == platform,
                Conversation.status.in_(["active", "handed_off"]),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, contact_id: uuid.UUID, platform: str = "website") -> Conversation:
        conversation = Conversation(
            id=uuid.uuid4(),
            contact_id=contact_id,
            platform=platform,
            status="active",
            ai_enabled=True,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def mark_handed_off(self, conversation: Conversation) -> Conversation:
        conversation.status = "handed_off"
        conversation.ai_enabled = False
        await self.db.flush()
        return conversation

    async def resume_ai(self, conversation: Conversation) -> Conversation:
        conversation.ai_enabled = True
        conversation.status = "active"
        await self.db.flush()
        return conversation
