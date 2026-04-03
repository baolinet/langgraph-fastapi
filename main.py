from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import users, auth
from database import engine
from models.user import Base
from utils.exceptions import register_exception_handlers
from utils.response import success_response

# 创建应用
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="FastAPI 实用三层架构示例 - 带认证功能"
)

# 注册异常处理器
register_exception_handlers(app)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(users.router)  # 用户路由

@app.get("/", tags=["系统"])
async def root():
    """API 根路径"""
    return success_response(
        data={
            "message": "欢迎使用 FastAPI 实用项目",
            "version": settings.app_version,
            "docs": "/docs"
        },
        message="欢迎"
    )

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return success_response(
        data={"status": "healthy"},
        message="健康检查通过"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )