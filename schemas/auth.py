from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class TokenResponse(BaseModel):
    """JWT Token 响应"""
    access_token: str  # JWT Token
    token_type: str = "bearer"
    expires_in: int = 3600  # 过期时间（秒）
    username: str
    user_id: int
    full_name: Optional[str] = None

class JWTPayload(BaseModel):
    """JWT Payload"""
    user_id: int
    username: str
    full_name: Optional[str] = None
    exp: Optional[datetime] = None

class AuthKeyResponse(BaseModel):
    """API Key 响应"""
    api_auth_key: str
    created_at: datetime
    expires_at: Optional[datetime] = None