from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "FastAPI 实用项目"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./agents.db"
    
    # JWT 配置
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60  # JWT 过期时间（分钟）

    # Agent / LLM 配置
    agent_default_llm: str = "default"
    agent_llm_configs: dict[str, dict[str, Any]] = {
        "default": {
            "model": "gemma4:e4b",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "temperature": 0.6,
            "max_tokens": None,
            "timeout": 60.0,
        }
    }

    # Legacy LLM 配置兼容
    provider: str | None = None
    llm_model_name: str | None = None
    temperature: float | None = None
    base_url: str | None = None
    api_key: str | None = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的环境变量

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "debug", "dev", "development"}:
                return True
            if lowered in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return bool(value)

    @field_validator("agent_llm_configs", mode="after")
    @classmethod
    def normalize_agent_llm_configs(cls, value: dict[str, dict[str, Any]], info) -> dict[str, dict[str, Any]]:
        data = info.data
        model_name = data.get("llm_model_name")
        base_url = data.get("base_url")
        api_key = data.get("api_key")
        legacy_temperature = data.get("temperature")

        base_default = dict(value.get("default", {}))
        if model_name:
            base_default["model"] = model_name
        if base_url:
            base_default["base_url"] = base_url
        if api_key:
            base_default["api_key"] = api_key
        if legacy_temperature is not None:
            base_default["temperature"] = float(legacy_temperature)

        base_default.setdefault("model", "gpt-4o-mini")
        base_default.setdefault("base_url", None)
        base_default.setdefault("api_key", None)
        base_default.setdefault("temperature", 0.3)
        base_default.setdefault("max_tokens", None)
        base_default.setdefault("timeout", 60.0)

        configs = dict(value)
        configs["default"] = base_default
        configs.setdefault(
            "creative",
            {
                **base_default,
                "temperature": 0.8,
            },
        )
        configs.setdefault(
            "strict_audit",
            {
                **base_default,
                "temperature": 0.1,
            },
        )
        configs.setdefault(
            "fast_support",
            {
                **base_default,
                "temperature": 0.2,
                "timeout": 45.0,
            },
        )
        return configs

@lru_cache()
def get_settings() -> Settings:
    """获取全局配置（单例）"""
    return Settings()
