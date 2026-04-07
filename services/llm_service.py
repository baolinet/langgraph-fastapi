from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from models.llm import AgentLLMBinding, LLMConfig


class LLMService:
    """LLM 配置查询服务。"""

    def __init__(self, db: Session):
        self.db = db

    def get_config_by_name(self, name: str) -> LLMConfig | None:
        return (
            self.db.query(LLMConfig)
            .filter(LLMConfig.name == name, LLMConfig.is_active.is_(True))
            .first()
        )

    def resolve_config(self, agent_type: str, llm_profile: str) -> dict[str, Any] | None:
        binding = self._find_agent_binding(agent_type, llm_profile)
        if binding:
            config = self.get_config_by_name(binding.llm_config_name)
            if config:
                return self._serialize_config(config, llm_profile)

        binding = self._find_profile_binding(llm_profile)
        if binding:
            config = self.get_config_by_name(binding.llm_config_name)
            if config:
                return self._serialize_config(config, llm_profile)

        fallback = (
            self.db.query(LLMConfig)
            .filter(LLMConfig.is_active.is_(True), LLMConfig.is_fallback.is_(True))
            .order_by(LLMConfig.id.asc())
            .first()
        )
        if fallback:
            return self._serialize_config(fallback, llm_profile)

        return None

    def _find_agent_binding(self, agent_type: str, llm_profile: str) -> AgentLLMBinding | None:
        return (
            self.db.query(AgentLLMBinding)
            .filter(
                AgentLLMBinding.is_active.is_(True),
                AgentLLMBinding.agent_type == agent_type,
                AgentLLMBinding.llm_profile == llm_profile,
            )
            .order_by(AgentLLMBinding.priority.asc(), AgentLLMBinding.id.asc())
            .first()
        )

    def _find_profile_binding(self, llm_profile: str) -> AgentLLMBinding | None:
        return (
            self.db.query(AgentLLMBinding)
            .filter(
                AgentLLMBinding.is_active.is_(True),
                AgentLLMBinding.agent_type.is_(None),
                AgentLLMBinding.llm_profile == llm_profile,
            )
            .order_by(AgentLLMBinding.priority.asc(), AgentLLMBinding.id.asc())
            .first()
        )

    @staticmethod
    def _serialize_config(config: LLMConfig, llm_profile: str) -> dict[str, Any]:
        return {
            "provider": config.provider,
            "model": config.model_name,
            "base_url": config.base_url,
            "api_key": config.api_key,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout,
            "llm_profile": llm_profile,
            "config_name": config.name,
            "source": "database",
        }
