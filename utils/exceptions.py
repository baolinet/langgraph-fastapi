from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from utils.response import error_response


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理 HTTP 异常"""
        return error_response(
            message=exc.detail,
            code=exc.status_code
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证异常"""
        errors = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "")
            errors.append(f"{field}: {msg}")
        
        return error_response(
            message="; ".join(errors),
            code=422
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未预料的异常"""
        return error_response(
            message=f"服务器内部错误：{str(exc)}",
            code=500
        )