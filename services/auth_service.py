from sqlalchemy.orm import Session
from models.user import User
from models.auth import AuthToken
from schemas.auth import LoginRequest
from typing import Optional
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from config import get_settings

settings = get_settings()

class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _generate_access_token() -> str:
        """生成访问 Token（随机字符串）"""
        return secrets.token_urlsafe(32)
    
    def create_jwt_token(self, user: User) -> str:
        """创建 JWT Token"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
        payload = {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    def verify_jwt_token(self, token: str) -> Optional[dict]:
        """验证 JWT Token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, login_request: LoginRequest) -> Optional[User]:
        """验证用户登录"""
        user = self.db.query(User).filter(
            User.username == login_request.username
        ).first()
        
        if not user:
            return None
        
        # 验证密码
        password_hash = self._hash_password(login_request.password)
        if user.password_hash != password_hash:
            return None
        
        # 检查用户是否激活
        if not user.is_active:
            return None
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """为用户创建 JWT Token"""
        return self.create_jwt_token(user)
    
    def create_api_auth_key(self, user_id: int, expires_hours: int = 24) -> AuthToken:
        """创建 API 认证 Key"""
        auth_token = AuthToken(
            user_id=user_id,
            api_auth_key=AuthToken.generate_key(),
            expires_at=AuthToken.create_expires_at(expires_hours)
        )
        self.db.add(auth_token)
        self.db.commit()
        self.db.refresh(auth_token)
        return auth_token
    
    def validate_api_auth_key(self, api_key: str) -> Optional[AuthToken]:
        """验证 API Key"""
        auth_token = self.db.query(AuthToken).filter(
            AuthToken.api_auth_key == api_key,
            AuthToken.is_active == True
        ).first()
        
        if not auth_token:
            return None
        
        # 检查是否过期（处理时区问题）
        if auth_token.expires_at:
            # 如果 expires_at 是 offset-naive，假设它是 UTC
            expires_at = auth_token.expires_at
            if expires_at.tzinfo is None:
                # 将 offset-naive 转换为 offset-aware（假设为 UTC）
                from datetime import timezone as tz
                expires_at = expires_at.replace(tzinfo=tz.utc)
            
            if expires_at < datetime.now(timezone.utc):
                auth_token.is_active = False
                self.db.commit()
                return None
        
        return auth_token
    
    def revoke_api_auth_key(self, api_key: str) -> bool:
        """撤销 API Key"""
        auth_token = self.db.query(AuthToken).filter(
            AuthToken.api_auth_key == api_key
        ).first()
        
        if not auth_token:
            return False
        
        auth_token.is_active = False
        self.db.commit()
        return True
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """通过 API Key 获取用户"""
        auth_token = self.validate_api_auth_key(api_key)
        if not auth_token:
            return None
        # 通过 user_id 逻辑关联查询用户
        return self.db.query(User).filter(User.id == auth_token.user_id).first()
    
    def get_user_by_jwt_token(self, token: str) -> Optional[User]:
        """通过 JWT Token 获取用户"""
        payload = self.verify_jwt_token(token)
        if not payload:
            return None
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return self.db.query(User).filter(User.id == user_id).first()