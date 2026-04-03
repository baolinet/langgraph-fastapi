from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from models.user import User
from typing import Optional

async def get_current_user_from_api_key(
    api_auth_key: Optional[str] = Header(None, alias="api-auth-key"),
    db: Session = Depends(get_db)
) -> User:
    """
    从 Header 中获取并验证 API Key
    
    在需要认证的接口中使用：
    @router.get("/protected", dependencies=[Depends(get_current_user_from_api_key)])
    """
    if not api_auth_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 api-auth-key 请求头",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_api_key(api_auth_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的或已过期的 API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def verify_api_auth_key(
    api_auth_key: Optional[str] = Header(None, alias="api-auth-key"),
    db: Session = Depends(get_db)
):
    """
    简单的 API Key 验证（不需要获取用户信息）
    
    在需要认证的接口中使用：
    @router.get("/protected", dependencies=[Depends(verify_api_auth_key)])
    """
    if not api_auth_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 api-auth-key 请求头",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    auth_service = AuthService(db)
    auth_token = auth_service.validate_api_auth_key(api_auth_key)
    
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的或已过期的 API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


async def get_current_user_from_jwt(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    从 Authorization Header 中获取并验证 JWT Token
    
    格式：Authorization: Bearer <jwt_token>
    
    在需要认证的接口中使用：
    @router.get("/protected", dependencies=[Depends(get_current_user_from_jwt)])
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Authorization 请求头",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 提取 Token
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证格式错误，应为：Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_jwt_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的或已过期的 JWT Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user