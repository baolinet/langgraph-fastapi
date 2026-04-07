from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from models.user import Base


class LLMConfig(Base):
    """LLM 连接配置"""

    __tablename__ = "llm_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    provider = Column(String(50), nullable=False, default="openai_compatible")
    model_name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    temperature = Column(Float, default=0.3)
    max_tokens = Column(Integer, nullable=True)
    timeout = Column(Float, default=60.0)
    is_active = Column(Boolean, default=True)
    is_fallback = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AgentLLMBinding(Base):
    """Agent 到 LLM 配置的绑定关系"""

    __tablename__ = "agent_llm_bindings"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(100), index=True, nullable=True)
    llm_profile = Column(String(100), index=True, nullable=False)
    llm_config_name = Column(String(100), index=True, nullable=False)
    priority = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
