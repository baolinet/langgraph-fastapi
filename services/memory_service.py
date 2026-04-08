from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from models.memory import AgentConversation, AgentMessage
from schemas.memory import AgentConversationCreate, AgentMessageCreate


class AgentMemoryService:
    """Agent 会话与消息存储服务。"""

    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, conversation_id: str) -> AgentConversation | None:
        return (
            self.db.query(AgentConversation)
            .filter(AgentConversation.conversation_id == conversation_id)
            .first()
        )

    def create_or_update_conversation(
        self, payload: AgentConversationCreate
    ) -> AgentConversation:
        conversation = self.get_conversation(payload.conversation_id)
        if conversation is None:
            conversation = AgentConversation(**payload.model_dump())
            self.db.add(conversation)
        else:
            data = payload.model_dump()
            for key, value in data.items():
                setattr(conversation, key, value)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def append_message(self, payload: AgentMessageCreate) -> AgentMessage:
        message = AgentMessage(
            conversation_id=payload.conversation_id,
            role=payload.role,
            content=payload.content,
            message_type=payload.message_type,
            status=payload.status,
            metadata_json=json.dumps(payload.metadata, ensure_ascii=False)
            if payload.metadata
            else None,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_messages(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        messages = (
            self.db.query(AgentMessage)
            .filter(AgentMessage.conversation_id == conversation_id)
            .order_by(AgentMessage.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._serialize_message(item) for item in messages]

    def update_waiting_status(
        self, conversation_id: str, *, status: str, waiting_for: str | None = None
    ) -> AgentConversation | None:
        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            return None
        conversation.status = status
        conversation.current_waiting_for = waiting_for
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    @staticmethod
    def _serialize_message(message: AgentMessage) -> dict[str, Any]:
        metadata = {}
        if message.metadata_json:
            metadata = json.loads(message.metadata_json)
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "message_type": message.message_type,
            "status": message.status,
            "metadata": metadata,
            "created_at": message.created_at,
        }
