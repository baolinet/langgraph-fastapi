from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from config import get_settings
from routers import agents, auth, users
from database import engine
from models import Base
from utils.exceptions import register_exception_handlers
from utils.response import success_response

# 创建应用
settings = get_settings()
static_dir = Path(__file__).parent / "static"
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="FastAPI 实用三层架构示例 - 带认证功能",
    docs_url=None,
    redoc_url=None,
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

# 挂载本地静态资源，避免文档依赖外部 CDN
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(users.router)  # 用户路由
app.include_router(agents.router)  # Agent 路由


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    """通过本地静态资源提供 Swagger UI。"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.app_name} - Swagger UI",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """通过本地静态资源提供 ReDoc。"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.app_name} - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
    )

@app.get("/", tags=["系统"])
async def root():
    """API 根路径"""
    return success_response(
        data={
            "message": "欢迎使用 FastAPI 实用项目",
            "version": settings.app_version,
            "docs": "/docs",
            "redoc": "/redoc",
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
