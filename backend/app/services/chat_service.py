"""
ChatService orchestrates the full message processing pipeline:
contact upsert → conversation management → dedup → classify → reply → handoff
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.contact import ContactRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.handoff_event import HandoffEventRepository
from app.repositories.lead_evaluation import LeadEvaluationRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.classifier import LeadClassifier
from app.services.reply_generator import ReplyGenerator

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.contacts = ContactRepository(db)
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.evaluations = LeadEvaluationRepository(db)
        self.handoffs = HandoffEventRepository(db)
        self.classifier = LeadClassifier()
        self.reply_gen = ReplyGenerator()

    async def process_message(self, req: ChatMessageRequest) -> ChatMessageResponse:
        # --- 1. Dedup check BEFORE any write ---
        existing_msg = await self.messages.get_by_external_id(req.external_message_id, req.platform)
        if existing_msg:
            return await self._build_duplicate_response(
                existing_msg.conversation_id, existing_msg.id
            )

        # --- 2. Upsert contact ---
        contact, _ = await self.contacts.get_or_create(
            external_user_id=req.external_user_id,
            name=req.name,
            email=str(req.email) if req.email else None,
            phone=req.phone,
            company_name=req.company_name,
        )

        # --- 3. Get or create conversation ---
        conversation = await self.conversations.get_active_for_contact(contact.id, req.platform)
        if conversation is None:
            conversation = await self.conversations.create(contact.id, req.platform)

        # --- 4. Save inbound message ---
        inbound = await self.messages.create(
            conversation_id=conversation.id,
            content=req.message,
            direction="inbound",
            sender_type="user",
            platform=req.platform,
            external_message_id=req.external_message_id,
        )

        # --- 5. Classify ---
        result = self.classifier.classify(
            req.message,
            contact_has_email=bool(contact.email),
            contact_has_phone=bool(contact.phone),
        )
        result.conversation_summary = f"User message: {req.message[:200]}"

        # --- 6. Persist evaluation ---
        eval_schema = result.to_schema()
        await self.evaluations.create(conversation.id, inbound.id, eval_schema)

        # --- 7. Generate reply (only if AI enabled) ---
        if conversation.ai_enabled:
            reply_text = self.reply_gen.generate(
                result,
                contact_name=contact.name,
                contact_email=contact.email,
                contact_phone=contact.phone,
            )
        else:
            reply_text = "Your conversation has been transferred to our team. A human agent will respond shortly."

        # --- 8. Save outbound reply ---
        outbound = await self.messages.create(
            conversation_id=conversation.id,
            content=reply_text,
            direction="outbound",
            sender_type="ai" if conversation.ai_enabled else "agent",
            platform=req.platform,
        )

        # --- 9. Handoff if required ---
        handoff_triggered = False
        if result.handoff_required and conversation.ai_enabled:
            handoff_triggered = True
            await self.handoffs.create(
                conversation_id=conversation.id,
                reason=result.handoff_reason or result.reason,
                handoff_type="sales",
            )
            await self.conversations.mark_handed_off(conversation)
            logger.info(
                "Handoff created for conversation %s, intent=%s", conversation.id, result.intent
            )

        await self.db.flush()

        return ChatMessageResponse(
            conversation_id=conversation.id,
            incoming_message_id=inbound.id,
            outgoing_message_id=outbound.id,
            duplicate=False,
            processing_status="processed",
            lead_evaluation=eval_schema,
            reply=reply_text,
            handoff_required=handoff_triggered,
            conversation_status=conversation.status,
        )

    async def _build_duplicate_response(
        self, conversation_id: uuid.UUID, incoming_message_id: uuid.UUID
    ) -> ChatMessageResponse:
        from app.schemas.lead import LeadEvaluationSchema

        # Return minimal response; no re-processing
        dummy_eval = LeadEvaluationSchema(
            is_lead=False,
            lead_temperature="not_lead",
            intent="duplicate",
            lead_score=0,
            confidence=1.0,
            reason="Duplicate message — already processed",
            handoff_required=False,
        )
        return ChatMessageResponse(
            conversation_id=conversation_id,
            incoming_message_id=incoming_message_id,
            outgoing_message_id=incoming_message_id,
            duplicate=True,
            processing_status="duplicate",
            lead_evaluation=dummy_eval,
            reply="",
            handoff_required=False,
            conversation_status="active",
        )
