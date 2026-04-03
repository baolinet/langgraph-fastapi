from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets

class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "FastAPI 实用项目"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./test.db"
    
    # JWT 配置
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60  # JWT 过期时间（分钟）
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的环境变量

@lru_cache()
def get_settings() -> Settings:
    """获取全局配置（单例）"""
    return Settings()