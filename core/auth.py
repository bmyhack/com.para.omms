from typing import Callable, List, Optional, Union, Any
from functools import wraps
import inspect
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

from .config import settings
from .exceptions import AuthenticationError, PermissionError
from .logger import error, debug

# OAuth2 密码流认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT 相关配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    """Token 数据模型"""
    sub: str
    exp: datetime
    user_id: int
    username: str
    roles: List[str] = []
    permissions: List[str] = []

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间
        
    Returns:
        JWT 令牌字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    从 JWT 令牌中获取当前用户信息
    
    Args:
        token: JWT 令牌
        
    Returns:
        当前用户的 TokenData
        
    Raises:
        AuthenticationError: 如果令牌无效或已过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(
            sub=payload.get("sub"),
            exp=datetime.fromtimestamp(payload.get("exp")),
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", [])
        )
        
        # 检查令牌是否过期
        if datetime.utcnow() > token_data.exp:
            raise AuthenticationError("令牌已过期")
            
        return token_data
    except JWTError as e:
        error(f"JWT 解析错误: {str(e)}")
        raise AuthenticationError("无效的认证凭据")

def require_auth(func: Callable = None):
    """
    要求用户认证的装饰器
    
    用法:
        @require_auth
        async def protected_route():
            return {"message": "这是受保护的路由"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取请求对象
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
                raise AuthenticationError("无法获取请求上下文")
            
            # 从请求头中获取 Authorization
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError("缺少认证令牌")
            
            token = auth_header.replace("Bearer ", "")
            
            # 验证令牌
            try:
                token_data = await get_current_user(token)
                # 将用户信息添加到请求状态
                request.state.user = token_data
                return await func(*args, **kwargs)
            except AuthenticationError as e:
                raise e
            except Exception as e:
                error(f"认证过程中发生错误: {str(e)}")
                raise AuthenticationError("认证失败")
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

def require_roles(roles: List[str]):
    """
    要求用户具有特定角色的装饰器
    
    Args:
        roles: 所需的角色列表
        
    用法:
        @require_roles(["admin", "manager"])
        async def admin_route():
            return {"message": "这是管理员路由"}
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
                raise PermissionError(f"需要以下角色之一: {', '.join(roles)}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permissions(permissions: List[str]):
    """
    要求用户具有特定权限的装饰器
    
    Args:
        permissions: 所需的权限列表
        
    用法:
        @require_permissions(["user:create", "user:update"])
        async def user_management_route():
            return {"message": "这是用户管理路由"}
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
            
            # 检查用户是否具有所需权限
            user_permissions = user.permissions
            if not all(perm in user_permissions for perm in permissions):
                raise PermissionError(f"需要以下权限: {', '.join(permissions)}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def is_superuser(func: Callable = None):
    """
    要求用户是超级管理员的装饰器
    
    用法:
        @is_superuser
        async def superuser_route():
            return {"message": "这是超级管理员路由"}
    """
    return require_roles(["superuser"])(func) if func else require_roles(["superuser"])

# 依赖项函数，可以在 FastAPI 路由中使用
async def get_current_user_dependency(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    获取当前用户的依赖项函数
    
    Args:
        token: JWT 令牌
        
    Returns:
        当前用户的 TokenData
    """
    return await get_current_user(token)

# 检查是否具有特定角色的依赖项
def has_roles(required_roles: List[str]):
    """
    检查用户是否具有特定角色的依赖项
    
    Args:
        required_roles: 所需的角色列表
        
    Returns:
        依赖项函数
    """
    async def dependency(user: TokenData = Depends(get_current_user_dependency)) -> TokenData:
        user_roles = user.roles
        if not any(role in user_roles for role in required_roles):
            raise PermissionError(f"需要以下角色之一: {', '.join(required_roles)}")
        return user
    return dependency

# 检查是否具有特定权限的依赖项
def has_permissions(required_permissions: List[str]):
    """
    检查用户是否具有特定权限的依赖项
    
    Args:
        required_permissions: 所需的权限列表
        
    Returns:
        依赖项函数
    """
    async def dependency(user: TokenData = Depends(get_current_user_dependency)) -> TokenData:
        user_permissions = user.permissions
        if not all(perm in user_permissions for perm in required_permissions):
            raise PermissionError(f"需要以下权限: {', '.join(required_permissions)}")
        return user
    return dependency

# 超级管理员依赖项
async def is_superuser_dependency(
    user: TokenData = Depends(get_current_user_dependency)
) -> TokenData:
    """
    检查用户是否是超级管理员的依赖项
    
    Args:
        user: 当前用户的 TokenData
        
    Returns:
        当前用户的 TokenData
    """
    if "superuser" not in user.roles:
        raise PermissionError("需要超级管理员权限")
    return user