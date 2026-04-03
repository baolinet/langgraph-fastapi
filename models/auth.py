from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()

class AuthToken(Base):
    """API 认证 Token 模型"""
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 逻辑关联，不使用 ForeignKey
    api_auth_key = Column(String(64), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    
    @classmethod
    def generate_key(cls) -> str:
        """生成随机 API Key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_expires_at(cls, hours: int = 24) -> datetime:
        """生成过期时间"""
        return datetime.now(timezone.utc) + timedelta(hours=hours)