from typing import Optional, Any, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime
import json


class APIResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = 200  # 状态码：200=成功，其他=错误
    message: str = "success"  # 消息
    data: Optional[Any] = None  # 数据
    timestamp: Optional[int] = None  # 时间戳
    
    class Config:
        arbitrary_types_allowed = True


class CustomJSONResponse(JSONResponse):
    """自定义 JSON 响应处理 datetime 序列化"""
    def render(self, content: any) -> bytes:
        def default_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=default_encoder,
        ).encode("utf-8")


def success_response(data: Any = None, message: str = "success", code: int = 200) -> CustomJSONResponse:
    """成功响应"""
    import time
    response = APIResponse(
        code=code,
        message=message,
        data=data,
        timestamp=int(time.time())
    )
    return CustomJSONResponse(content=response.model_dump())


def error_response(message: str = "error", code: int = 400, data: Any = None) -> CustomJSONResponse:
    """错误响应"""
    import time
    response = APIResponse(
        code=code,
        message=message,
        data=data,
        timestamp=int(time.time())
    )
    return CustomJSONResponse(content=response.model_dump(), status_code=code)