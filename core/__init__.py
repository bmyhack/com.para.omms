from .logger import debug, info, error
from .db import get_db
from .config import settings
from .events import register_events
from .api import api_router
from .responses import (
    ResponseCode, ResponseModel, PaginationModel,
    success_response, error_response, pagination_response, APIResponse
)
from .exceptions import (
    APIException, ParameterError, AuthenticationError, PermissionError,
    NotFoundError, BusinessError, DatabaseError, register_exception_handlers
)
from .auth import (
    create_access_token, get_current_user, require_auth, require_roles,
    require_permissions, is_superuser, get_current_user_dependency,
    has_roles, has_permissions, is_superuser_dependency
)

# 可以添加 __all__ 来控制 from core import * 的行为
__all__ = [
    # 日志
    'debug', 'info', 'error',
    # 数据库
    'get_db',
    # 配置
    'settings',
    # 事件
    'register_events',
    # 路由
    'api_router',
    # 响应
    'ResponseCode', 'ResponseModel', 'PaginationModel',
    'success_response', 'error_response', 'pagination_response', 'APIResponse',
    # 异常
    'APIException', 'ParameterError', 'AuthenticationError', 'PermissionError',
    'NotFoundError', 'BusinessError', 'DatabaseError', 'register_exception_handlers',
    # 认证
    'create_access_token', 'get_current_user', 'require_auth', 'require_roles',
    'require_permissions', 'is_superuser', 'get_current_user_dependency',
    'has_roles', 'has_permissions', 'is_superuser_dependency'
]