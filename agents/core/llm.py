from __future__ import annotations

from typing import Any

from config import get_settings
from database import SessionLocal
from agents.profiles.base import AgentProfile
from services.llm_service import LLMService


def get_all_llm_configs() -> dict[str, dict[str, Any]]:
    settings = get_settings()
    configs = settings.agent_llm_configs or {}
    if settings.agent_default_llm not in configs:
        raise ValueError(
            f"Default LLM profile '{settings.agent_default_llm}' is not defined in agent_llm_configs."
        )
    return configs


def get_default_llm_config() -> dict[str, Any]:
    settings = get_settings()
    return dict(get_all_llm_configs()[settings.agent_default_llm])


def get_llm_config(profile: AgentProfile) -> dict[str, Any]:
    settings = get_settings()
    llm_profile = profile.llm_profile or settings.agent_default_llm

    db_config = _get_db_llm_config(profile.agent_type, llm_profile)
    if db_config:
        config = dict(db_config)
        config.update(profile.model_config)
        return config

    all_configs = get_all_llm_configs()
    if llm_profile not in all_configs:
        available = ", ".join(sorted(all_configs))
        raise ValueError(
            f"Unknown llm profile '{llm_profile}' for agent '{profile.agent_type}'. "
            f"Available profiles: {available}"
        )
    config = dict(all_configs[llm_profile])
    config.update(profile.model_config)
    config["llm_profile"] = llm_profile
    config["source"] = "settings"
    return config


def create_chat_model(profile: AgentProfile):
    config = get_llm_config(profile)
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "langchain-openai is not installed. Install it before enabling live LLM calls."
        ) from exc

    kwargs = {
        "model": config["model"],
        "temperature": config["temperature"],
        "timeout": config["timeout"],
    }
    if config.get("base_url"):
        kwargs["base_url"] = config["base_url"]
    if config.get("api_key"):
        kwargs["api_key"] = config["api_key"]
    if config.get("max_tokens") is not None:
        kwargs["max_tokens"] = config["max_tokens"]
    return ChatOpenAI(**kwargs)


def _get_db_llm_config(agent_type: str, llm_profile: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        service = LLMService(db)
        return service.resolve_config(agent_type=agent_type, llm_profile=llm_profile)
    finally:
        db.close()
