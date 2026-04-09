from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse, UserChangePassword
from routers.dependencies import get_current_user_from_api_key, verify_api_auth_key
from models.user import User
from typing import List, Optional
from utils.response import success_response, error_response
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])

def serialize_user(user: User) -> dict:
    """将 SQLAlchemy User 对象序列化为字典"""
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """依赖注入：获取 UserService"""
    return UserService(db)

@router.get("/", summary="获取所有用户", dependencies=[Depends(verify_api_auth_key)])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_service: UserService = Depends(get_user_service)
):
    """获取所有用户列表（支持分页）"""
    users = user_service.get_all_users(skip=skip, limit=limit)
    return success_response(data=[
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        for user in users
    ], message="获取用户列表成功")


@router.post("/change-password", summary="修改当前用户密码")
async def change_password(
    password_change: UserChangePassword,
    current_user: User = Depends(get_current_user_from_api_key),
    user_service: UserService = Depends(get_user_service)
):
    """使用 api-auth-key 修改当前登录用户密码"""
    try:
        user_service.change_password(current_user, password_change)
        return success_response(message="密码修改成功")
    except ValueError as e:
        return error_response(message=str(e), code=400)

@router.get("/{username}", summary="获取用户详情", dependencies=[Depends(verify_api_auth_key)])
async def get_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    """根据用户名获取用户详情"""
    user = user_service.get_user_by_username(username)
    if not user:
        return error_response(message=f"用户名 {username} 不存在", code=404)
    return success_response(data=serialize_user(user), message="获取用户详情成功")

@router.get("/search/fullname/{fullname}", summary="根据全名模糊查询", dependencies=[Depends(verify_api_auth_key)])
async def search_by_fullname(
    fullname: str,
    user_service: UserService = Depends(get_user_service)
):
    """根据全名进行左侧模糊匹配查询（LIKE 'fullname%'）"""
    users = user_service.search_users_by_fullname(fullname)
    if not users:
        return error_response(message=f"未找到匹配全名 '{fullname}' 的用户", code=404)
    return success_response(data=[serialize_user(user) for user in users], message="查询用户成功")

@router.post("/", status_code=status.HTTP_201_CREATED, summary="创建用户", dependencies=[Depends(verify_api_auth_key)])
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """创建新用户"""
    try:
        user = user_service.create_user(user_create)
        return success_response(data=serialize_user(user), message="用户创建成功", code=201)
    except ValueError as e:
        return error_response(message=str(e), code=400)

@router.put("/{username}", summary="更新用户", dependencies=[Depends(verify_api_auth_key)])
async def update_user(
    username: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息"""
    try:
        user = user_service.update_user_by_username(username, user_update)
        if not user:
            return error_response(message=f"用户名 {username} 不存在", code=404)
        return success_response(data=serialize_user(user), message="用户更新成功")
    except ValueError as e:
        return error_response(message=str(e), code=400)

@router.delete("/{username}", summary="删除用户", dependencies=[Depends(verify_api_auth_key)])
async def delete_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    """删除用户"""
    success = user_service.delete_user_by_username(username)
    if not success:
        return error_response(message=f"用户名 {username} 不存在", code=404)
    return success_response(message="用户删除成功")

@router.post("/{username}/activate", summary="激活用户", dependencies=[Depends(verify_api_auth_key)])
async def activate_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    """激活已禁用的用户"""
    user = user_service.activate_user_by_username(username)
    if not user:
        return error_response(message=f"用户名 {username} 不存在", code=404)
    return success_response(data=serialize_user(user), message="用户激活成功")

@router.post("/{username}/deactivate", summary="禁用用户", dependencies=[Depends(verify_api_auth_key)])
async def deactivate_user(
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    """禁用用户"""
    user = user_service.deactivate_user_by_username(username)
    if not user:
        return error_response(message=f"用户名 {username} 不存在", code=404)
    return success_response(data=serialize_user(user), message="用户禁用成功")
