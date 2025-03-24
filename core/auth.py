from typing import Callable, List, Optional, Union, Any, Dict
from functools import wraps
import inspect
from fastapi import Depends, HTTPException, status, Request, Form, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from .config import settings
from .exceptions import AuthenticationError, PermissionError

# JWT相关配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# OAuth2密码流认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 令牌数据模型
class TokenData(BaseModel):
    user_id: int
    username: str
    roles: List[str] = []
    permissions: List[str] = []
    exp: Optional[datetime] = None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间增量，如果为None则使用默认值
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 创建JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str) -> TokenData:
    """
    从JWT令牌中获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        令牌数据对象
        
    Raises:
        AuthenticationError: 如果令牌无效或已过期
    """
    try:
        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 提取用户信息
        user_id = payload.get("user_id")
        username = payload.get("sub")
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])
        exp = payload.get("exp")
        
        if username is None or user_id is None:
            raise AuthenticationError("无效的令牌")
        
        # 创建令牌数据对象
        token_data = TokenData(
            user_id=user_id,
            username=username,
            roles=roles,
            permissions=permissions,
            exp=datetime.fromtimestamp(exp) if exp else None
        )
        return token_data
    except JWTError:
        raise AuthenticationError("无效的令牌")

# 依赖项函数，用于获取当前用户
async def get_current_user_dependency(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    获取当前用户的依赖项
    
    Args:
        token: JWT令牌
        
    Returns:
        令牌数据对象
    """
    return await get_current_user(token)

# 认证装饰器
def require_auth(func: Callable):
    """
    要求用户认证的装饰器
    
    用法:
        @require_auth
        async def protected_route():
            return {"message": "受保护的路由"}
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 查找请求对象
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for _, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break
        
        if not request:
            # 如果找不到请求对象，尝试从依赖项中获取
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param.annotation == Request:
                    # 创建一个新的请求对象
                    request = Request(scope={"type": "http"})
                    kwargs[param_name] = request
                    break
        
        if not request:
            raise AuthenticationError("无法获取请求对象")
        
        # 获取认证头
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("缺少认证令牌")
        
        # 提取令牌
        token = auth_header.replace("Bearer ", "")
        
        # 验证令牌并获取用户信息
        user = await get_current_user(token)
        
        # 将用户信息添加到请求状态
        request.state.user = user
        
        return await func(*args, **kwargs)
    return wrapper

# 角色装饰器
def require_roles(roles: List[str]):
    """
    要求用户具有特定角色的装饰器
    
    Args:
        roles: 所需的角色列表
        
    用法:
        @require_roles(["admin", "manager"])
        async def admin_route():
            return {"message": "管理员路由"}
    """
    def decorator(func: Callable):
        @wraps(func)
        @require_auth
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for _, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request or not hasattr(request.state, "user"):
                raise AuthenticationError("用户未认证")
            
            user = request.state.user
            
            # 检查用户是否具有所需角色
            user_roles = user.roles
            if not any(role in user_roles for role in roles):
                raise PermissionError(f"需要角色: {', '.join(roles)}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 超级管理员装饰器
def is_superuser(func: Callable):
    """
    要求用户是超级管理员的装饰器
    
    用法:
        @is_superuser
        async def superuser_route():
            return {"message": "超级管理员路由"}
    """
    @wraps(func)
    @require_auth
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for _, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break
        
        if not request or not hasattr(request.state, "user"):
            raise AuthenticationError("用户未认证")
        
        user = request.state.user
        
        # 检查用户是否是超级管理员
        if "superuser" not in user.roles:
            raise PermissionError("需要超级管理员权限")
        
        return await func(*args, **kwargs)
    return wrapper

# 添加更多的权限验证装饰器
def require_permission(permission_code: str):
    """
    要求用户具有特定权限的装饰器
    
    Args:
        permission_code: 所需的权限代码
        
    用法:
        @require_permission("user:create")
        async def create_user_route():
            return {"message": "创建用户成功"}
    """
    def decorator(func: Callable):
        @wraps(func)
        @require_auth
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for _, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request or not hasattr(request.state, "user"):
                raise AuthenticationError("用户未认证")
            
            user = request.state.user
            
            # 超级管理员拥有所有权限
            if "superuser" in user.roles:
                return await func(*args, **kwargs)
            
            # 检查用户是否具有所需权限
            user_permissions = user.permissions
            if permission_code not in user_permissions:
                raise PermissionError(f"需要权限: {permission_code}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 依赖项函数，检查是否具有特定权限
def has_permission(permission_code: str):
    """
    检查用户是否具有特定权限的依赖项
    
    Args:
        permission_code: 所需的权限代码
        
    Returns:
        依赖项函数
    """
    async def dependency(user: TokenData = Depends(get_current_user_dependency)) -> TokenData:
        # 超级管理员拥有所有权限
        if "superuser" in user.roles:
            return user
            
        user_permissions = user.permissions
        if permission_code not in user_permissions:
            raise PermissionError(f"需要权限: {permission_code}")
        return user
    return dependency

# 添加API路由权限验证中间件
class PermissionMiddleware:
    """
    API路由权限验证中间件
    """
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # 创建请求对象
        request = Request