from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LLMConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(default="openai_compatible")
    model_name: str = Field(..., min_length=1, max_length=100)
    base_url: str | None = None
    api_key: str | None = None
    temperature: float = 0.3
    max_tokens: int | None = None
    timeout: float = 60.0
    is_active: bool = True
    is_fallback: bool = False


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigResponse(LLMConfigBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentLLMBindingBase(BaseModel):
    agent_type: str | None = None
    llm_profile: str = Field(..., min_length=1, max_length=100)
    llm_config_name: str = Field(..., min_length=1, max_length=100)
    priority: int = 100
    is_active: bool = True


class AgentLLMBindingCreate(AgentLLMBindingBase):
    pass


class AgentLLMBindingResponse(AgentLLMBindingBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
