from typing import Any, Dict, Optional, Union, List
from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from .responses import ResponseCode, error_response
from .logger import error, exception

class APIException(Exception):
    """API 异常基类"""
    
    def __init__(
        self,
        code: str = ResponseCode.SERVER_ERROR,
        message: str = "服务器内部错误",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Any = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)

class ParameterError(APIException):
    """参数错误"""
    
    def __init__(self, message: str = "参数错误", data: Any = None):
        super().__init__(
            code=ResponseCode.PARAM_ERROR,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )

class AuthenticationError(APIException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败", data: Any = None):
        super().__init__(
            code=ResponseCode.UNAUTHORIZED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            data=data
        )

class PermissionError(APIException):
    """权限错误"""
    
    def __init__(self, message: str = "权限不足", data: Any = None):
        super().__init__(
            code=ResponseCode.FORBIDDEN,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            data=data
        )

class NotFoundError(APIException):
    """资源不存在"""
    
    def __init__(self, message: str = "资源不存在", data: Any = None):
        super().__init__(
            code=ResponseCode.NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )

class BusinessError(APIException):
    """业务错误"""
    
    def __init__(self, message: str = "业务处理失败", data: Any = None):
        super().__init__(
            code=ResponseCode.BUSINESS_ERROR,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )

class DatabaseError(APIException):
    """数据库错误"""
    
    def __init__(self, message: str = "数据库操作失败", data: Any = None):
        super().__init__(
            code=ResponseCode.SERVER_ERROR,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data=data
        )

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    API 异常处理器
    
    Args:
        request: 请求对象
        exc: API 异常
        
    Returns:
        统一格式的 JSON 响应
    """
    error(f"API异常: {exc.message}, 路径: {request.url.path}, 状态码: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            data=exc.data
        )
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP 异常
        
    Returns:
        统一格式的 JSON 响应
    """
    error(f"HTTP异常: {exc.detail}, 路径: {request.url.path}, 状态码: {exc.status_code}")
    
    # 根据状态码映射到响应码
    code_map = {
        400: ResponseCode.PARAM_ERROR,
        401: ResponseCode.UNAUTHORIZED,
        403: ResponseCode.FORBIDDEN,
        404: ResponseCode.NOT_FOUND,
        405: ResponseCode.METHOD_NOT_ALLOWED,
        500: ResponseCode.SERVER_ERROR,
        503: ResponseCode.SERVICE_UNAVAILABLE,
        504: ResponseCode.GATEWAY_TIMEOUT
    }
    
    code = code_map.get(exc.status_code, ResponseCode.SERVER_ERROR)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=code,
            message=str(exc.detail),
            data=None
        ),
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    请求验证异常处理器
    
    Args:
        request: 请求对象
        exc: 验证异常
        
    Returns:
        统一格式的 JSON 响应
    """
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": " -> ".join([str(loc) for loc in error["loc"]]),
            "msg": error["msg"],
            "type": error["type"]
        })
    
    error_msg = "请求参数验证失败"
    error(f"{error_msg}, 路径: {request.url.path}, 详情: {error_details}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            code=ResponseCode.PARAM_ERROR,
            message=error_msg,
            data=error_details
        )
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    SQLAlchemy 异常处理器
    
    Args:
        request: 请求对象
        exc: SQLAlchemy 异常
        
    Returns:
        统一格式的 JSON 响应
    """
    error_msg = "数据库操作失败"
    exception(f"{error_msg}, 路径: {request.url.path}, 异常: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code=ResponseCode.SERVER_ERROR,
            message=error_msg,
            data=None
        )
    )

async def python_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用 Python 异常处理器
    
    Args:
        request: 请求对象
        exc: Python 异常
        
    Returns:
        统一格式的 JSON 响应
    """
    error_msg = "服务器内部错误"
    exception(f"{error_msg}, 路径: {request.url.path}, 异常: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code=ResponseCode.SERVER_ERROR,
            message=error_msg,
            data=None
        )
    )

def register_exception_handlers(app):
    """
    注册所有异常处理器
    
    Args:
        app: FastAPI 应用实例
    """
    # 注册自定义 API 异常处理器
    app.add_exception_handler(APIException, api_exception_handler)
    
    # 注册 HTTP 异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 注册请求验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 注册 SQLAlchemy 异常处理器
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # 注册通用 Python 异常处理器
    app.add_exception_handler(Exception, python_exception_handler)