from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from models.user import Base


class AgentConversation(Base):
    """Agent 会话记录。"""

    __tablename__ = "agent_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, index=True, nullable=False)
    agent_type = Column(String(100), index=True, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    title = Column(String(200), nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    current_waiting_for = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AgentMessage(Base):
    """Agent 消息记录。"""

    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        String(100),
        ForeignKey("agent_conversations.conversation_id"),
        index=True,
        nullable=False,
    )
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text", nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
