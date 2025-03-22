from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from enum import Enum
import time

# 定义泛型类型变量
T = TypeVar('T')

class ResponseCode(str, Enum):
    """响应状态码枚举"""
    SUCCESS = "0"               # 成功
    PARAM_ERROR = "400"         # 参数错误
    UNAUTHORIZED = "401"        # 未授权
    FORBIDDEN = "403"           # 禁止访问
    NOT_FOUND = "404"           # 资源不存在
    METHOD_NOT_ALLOWED = "405"  # 方法不允许
    SERVER_ERROR = "500"        # 服务器错误
    SERVICE_UNAVAILABLE = "503" # 服务不可用
    GATEWAY_TIMEOUT = "504"     # 网关超时
    BUSINESS_ERROR = "600"      # 业务错误

class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: str = Field(ResponseCode.SUCCESS, description="响应状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000), description="时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "0",
                "message": "操作成功",
                "data": None,
                "timestamp": 1625123456789
            }
        }

class PaginationModel(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页大小")
    pages: int = Field(1, description="总页数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 10,
                "pages": 0
            }
        }

def success_response(*, data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        
    Returns:
        统一格式的响应字典
    """
    return ResponseModel(
        code=ResponseCode.SUCCESS,
        message=message,
        data=data
    ).dict()

def error_response(*, code: str = ResponseCode.SERVER_ERROR, message: str = "操作失败", data: Any = None) -> Dict[str, Any]:
    """
    错误响应
    
    Args:
        code: 错误代码
        message: 错误消息
        data: 错误详情数据
        
    Returns:
        统一格式的响应字典
    """
    return ResponseModel(
        code=code,
        message=message,
        data=data
    ).dict()

def pagination_response(
    items: List[Any],
    total: int,
    page: int = 1,
    size: int = 10,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """
    分页响应
    
    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        size: 每页大小
        message: 响应消息
        
    Returns:
        统一格式的分页响应字典
    """
    pages = (total + size - 1) // size if size > 0 else 0
    
    pagination = PaginationModel(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
    
    return ResponseModel(
        code=ResponseCode.SUCCESS,
        message=message,
        data=pagination
    ).dict()

class APIResponse(JSONResponse):
    """自定义 API 响应类"""
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None:
        if not isinstance(content, dict) or not all(k in content for k in ("code", "message", "timestamp")):
            content = success_response(data=content)
        
        super().__init__(
            content=jsonable_encoder(content),
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )