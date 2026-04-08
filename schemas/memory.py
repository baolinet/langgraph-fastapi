from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentConversationBase(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., min_length=1, max_length=100)
    status: str = "active"
    title: str | None = None
    user_id: int | None = None
    current_waiting_for: str | None = None
    summary: str | None = None
    is_active: bool = True


class AgentConversationCreate(AgentConversationBase):
    pass


class AgentConversationResponse(AgentConversationBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMessageBase(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    message_type: str = "text"
    status: str = "completed"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMessageCreate(AgentMessageBase):
    pass


class AgentMessageResponse(AgentMessageBase):
    id: int
    created_at: datetime | None = None
