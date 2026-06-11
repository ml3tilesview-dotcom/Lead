import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.conversation import ConversationRepository
from app.repositories.handoff_event import HandoffEventRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationMessagesResponse,
    ConversationResponse,
    MessageSchema,
)
from app.schemas.handoff import HandoffRequest, HandoffResponse

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def _get_conversation_or_404(conv):
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    repo = ConversationRepository(db)
    conv = _get_conversation_or_404(await repo.get_by_id(conversation_id))
    return ConversationResponse.model_validate(conv)


@router.get("/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationMessagesResponse:
    conv_repo = ConversationRepository(db)
    _get_conversation_or_404(await conv_repo.get_by_id(conversation_id))

    msg_repo = MessageRepository(db)
    msgs = await msg_repo.get_conversation_messages(conversation_id)
    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=[MessageSchema.model_validate(m) for m in msgs],
        total=len(msgs),
    )


@router.post("/{conversation_id}/handoff", response_model=HandoffResponse)
async def manual_handoff(
    conversation_id: uuid.UUID,
    body: HandoffRequest,
    db: AsyncSession = Depends(get_db),
) -> HandoffResponse:
    conv_repo = ConversationRepository(db)
    conv = _get_conversation_or_404(await conv_repo.get_by_id(conversation_id))

    handoff_repo = HandoffEventRepository(db)
    event = await handoff_repo.create(
        conversation_id=conv.id,
        reason=body.reason,
        handoff_type=body.handoff_type,
        notes=body.notes,
    )
    await conv_repo.mark_handed_off(conv)
    await db.commit()
    await db.refresh(event)

    return HandoffResponse(
        handoff_event_id=event.id,
        conversation_id=conv.id,
        status=event.status,
        reason=event.reason,
        created_at=event.created_at,
    )


@router.post("/{conversation_id}/resume-ai", response_model=ConversationResponse)
async def resume_ai(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    repo = ConversationRepository(db)
    conv = _get_conversation_or_404(await repo.get_by_id(conversation_id))
    conv = await repo.resume_ai(conv)
    await db.commit()
    # Refresh to reload server-side timestamps after commit (avoids greenlet error)
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)
