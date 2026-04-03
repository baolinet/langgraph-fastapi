from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from services.user_service import UserService
from schemas.auth import LoginRequest, TokenResponse, AuthKeyResponse
from config import get_settings
from typing import Optional
from datetime import datetime
from utils.response import success_response, error_response

settings = get_settings()

router = APIRouter(tags=["authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """依赖注入：获取 AuthService"""
    return AuthService(db)

@router.post("/login", summary="用户登录")
async def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用户登录获取 JWT Token
    
    - **username**: 用户名
    - **password**: 密码
    - 返回的 JWT Token 包含用户 ID、用户名等基础信息，供前端 Web 应用使用
    """
    user = auth_service.authenticate_user(login_request)
    if not user:
        return error_response(message="用户名或密码错误", code=401)
    
    # 创建 JWT Token
    jwt_token = auth_service.create_jwt_token(user)
    
    token_data = TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        username=user.username,
        user_id=user.id,
        full_name=user.full_name
    )
    
    return success_response(data=token_data.model_dump(), message="登录成功")

@router.post("/api-key", summary="创建 API Key")
async def create_api_key(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    创建 API 认证 Key
    
    - **username**: 用户名
    - **password**: 密码
    - 返回的 api_auth_key 用于访问 /api/** 接口
    """
    user = auth_service.authenticate_user(login_request)
    if not user:
        return error_response(message="用户名或密码错误", code=401)
    
    auth_token = auth_service.create_api_auth_key(user.id, expires_hours=24)
    
    api_key_data = AuthKeyResponse(
        api_auth_key=auth_token.api_auth_key,
        created_at=auth_token.created_at,
        expires_at=auth_token.expires_at
    )
    
    return success_response(data=api_key_data.model_dump(), message="API Key 创建成功")

@router.post("/api-key/revoke", summary="撤销 API Key")
async def revoke_api_key(
    api_auth_key: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    撤销 API Key
    
    - **api_auth_key**: 要撤销的 API Key
    """
    success = auth_service.revoke_api_auth_key(api_auth_key)
    if not success:
        return error_response(message="API Key 不存在", code=404)
    return success_response(message="API Key 已撤销")