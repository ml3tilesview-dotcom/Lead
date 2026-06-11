import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_external_id(self, external_message_id: str, platform: str) -> Message | None:
        result = await self.db.execute(
            select(Message).where(
                Message.external_message_id == external_message_id,
                Message.platform == platform,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        conversation_id: uuid.UUID,
        content: str,
        direction: str,
        sender_type: str,
        platform: str = "website",
        external_message_id: str | None = None,
    ) -> Message:
        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            content=content,
            direction=direction,
            sender_type=sender_type,
            platform=platform,
            external_message_id=external_message_id,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_conversation_messages(self, conversation_id: uuid.UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())
