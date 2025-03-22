from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from core.db import get_db
from core.responses import success_response, pagination_response
from core.auth import (
    require_auth, require_roles, require_permissions, is_superuser,
    create_access_token
)
from core.exceptions import AuthenticationError, NotFoundError
from .schemas import (
    User, UserCreate, UserUpdate, UserLogin, Token,
    Role, RoleCreate, RoleUpdate,
    Permission, PermissionCreate, PermissionUpdate
)
from .services import (
    # 用户服务
    get_user, get_users, create_user, update_user, delete_user,
    authenticate_user, update_last_login, get_user_permissions,
    # 角色服务
    get_role, get_roles, create_role, update_role, delete_role,
    assign_role_to_user, remove_role_from_user,
    # 权限服务
    get_permission, get_permissions, create_permission, update_permission, delete_permission,
    assign_permission_to_role, remove_permission_from_role
)

router = APIRouter()

# 认证相关路由
@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise AuthenticationError("用户名或密码错误")
    
    if not user.is_active:
        raise AuthenticationError("用户已被禁用")
    
    # 获取用户权限
    permissions = await get_user_permissions(db, user.id)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    # 修改这里：移除 await 关键字
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "username": user.username,
            "roles": [role.name for role in user.roles],
            "permissions": permissions
        },
        expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    await update_last_login(db, user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds,
        "user_id": user.id,
        "username": user.username
    }

@router.get("/me", response_model=User)
@require_auth
async def read_users_me(request: Request, db: AsyncSession = Depends(get_db)):
    """获取当前用户信息"""
    user_id = request.state.user.user_id
    user = await get_user(db, user_id)
    if not user:
        raise NotFoundError("用户不存在")
    return user

# 用户管理路由
@router.get("/users", response_model=List[User])
@require_permissions(["user:list"])
async def read_users(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    username: Optional[str] = Query(None, description="用户名过滤"),
    email: Optional[str] = Query(None, description="邮箱过滤"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    is_superuser: Optional[bool] = Query(None, description="是否超级管理员"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    filters = {}
    if username:
        filters["username"] = username
    if email:
        filters["email"] = email
    if is_active is not None:
        filters["is_active"] = is_active
    if is_superuser is not None:
        filters["is_superuser"] = is_superuser
    
    users = await get_users(db, skip=skip, limit=limit, filters=filters)
    return users

@router.post("/users", response_model=User)
@require_permissions(["user:create"])
async def create_user_route(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    return await create_user(db, user_in)

@router.get("/users/{user_id}", response_model=User)
@require_permissions(["user:read"])
async def read_user(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    user = await get_user(db, user_id)
    if not user:
        raise NotFoundError("用户不存在")
    return user

@router.put("/users/{user_id}", response_model=User)
@require_permissions(["user:update"])
async def update_user_route(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    user_in: UserUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    return await update_user(db, user_id, user_in)

@router.delete("/users/{user_id}")
@require_permissions(["user:delete"])
async def delete_user_route(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    await delete_user(db, user_id)
    return success_response(message="用户删除成功")

# 角色管理路由
@router.get("/roles", response_model=List[Role])
@require_permissions(["role:list"])
async def read_roles(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    name: Optional[str] = Query(None, description="角色名称过滤"),
    db: AsyncSession = Depends(get_db)
):
    """获取角色列表"""
    roles = await get_roles(db, skip=skip, limit=limit, name=name)
    return roles

@router.post("/roles", response_model=Role)
@require_permissions(["role:create"])
async def create_role_route(
    request: Request,
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    return await create_role(db, role_in)

@router.get("/roles/{role_id}", response_model=Role)
@require_permissions(["role:read"])
async def read_role(
    request: Request,
    role_id: int = Path(..., ge=1, description="角色ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取角色详情"""
    role = await get_role(db, role_id)
    if not role:
        raise NotFoundError("角色不存在")
    return role

@router.put("/roles/{role_id}", response_model=Role)
@require_permissions(["role:update"])
async def update_role_route(
    request: Request,
    role_id: int = Path(..., ge=1, description="角色ID"),
    role_in: RoleUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """更新角色信息"""
    return await update_role(db, role_id, role_in)

@router.delete("/roles/{role_id}")
@require_permissions(["role:delete"])
async def delete_role_route(
    request: Request,
    role_id: int = Path(..., ge=1, description="角色ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    await delete_role(db, role_id)
    return success_response(message="角色删除成功")

# 用户角色管理
@router.post("/users/{user_id}/roles/{role_id}")
@require_permissions(["user:assign_role"])
async def assign_role_to_user_route(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    role_id: int = Path(..., ge=1, description="角色ID"),
    db: AsyncSession = Depends(get_db)
):
    """为用户分配角色"""
    await assign_role_to_user(db, user_id, role_id)
    return success_response(message="角色分配成功")

@router.delete("/users/{user_id}/roles/{role_id}")
@require_permissions(["user:remove_role"])
async def remove_role_from_user_route(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    role_id: int = Path(..., ge=1, description="角色ID"),
    db: AsyncSession = Depends(get_db)
):
    """从用户移除角色"""
    await remove_role_from_user(db, user_id, role_id)
    return success_response(message="角色移除成功")

# 权限管理路由
@router.get("/permissions", response_model=List[Permission])
@require_permissions(["permission:list"])
async def read_permissions(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    code: Optional[str] = Query(None, description="权限代码过滤"),
    name: Optional[str] = Query(None, description="权限名称过滤"),
    db: AsyncSession = Depends(get_db)
):
    """获取权限列表"""
    permissions = await get_permissions(db, skip=skip, limit=limit, code=code, name=name)
    return permissions

@router.post("/permissions", response_model=Permission)
@require_permissions(["permission:create"])
async def create_permission_route(
    request: Request,
    permission_in: PermissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建权限"""
    return await create_permission(db, permission_in)

@router.get("/permissions/{permission_id}", response_model=Permission)
@require_permissions(["permission:read"])
async def read_permission(
    request: Request,
    permission_id: int = Path(..., ge=1, description="权限ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取权限详情"""
    permission = await get_permission(db, permission_id)
    if not permission:
        raise NotFoundError("权限不存在")
    return permission

@router.put("/permissions/{permission_id}", response_model=Permission)
@require_permissions(["permission:update"])
async def update_permission_route(
    request: Request,
    permission_id: int = Path(..., ge=1, description="权限ID"),
    permission_in: PermissionUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """更新权限信息"""
    return await update_permission(db, permission_id, permission_in)

@router.delete("/permissions/{permission_id}")
@require_permissions(["permission:delete"])
async def delete_permission_route(
    request: Request,
    permission_id: int = Path(..., ge=1, description="权限ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除权限"""
    await delete_permission(db, permission_id)
    return success_response(message="权限删除成功")

# 角色权限管理
@router.post("/roles/{role_id}/permissions/{permission_id}")
@require_permissions(["role:assign_permission"])
async def assign_permission_to_role_route(
    request: Request,
    role_id: int = Path(..., ge=1, description="角色ID"),
    permission_id: int = Path(..., ge=1, description="权限ID"),
    db: AsyncSession = Depends(get_db)
):
    """为角色分配权限"""
    await assign_permission_to_role(db, role_id, permission_id)
    return success_response(message="权限分配成功")

@router.delete("/roles/{role_id}/permissions/{permission_id}")
@require_permissions(["role:remove_permission"])
async def remove_permission_from_role_route(
    request: Request,
    role_id: int = Path(..., ge=1, description="角色ID"),
    permission_id: int = Path(..., ge=1, description="权限ID"),
    db: AsyncSession = Depends(get_db)
):
    """从角色移除权限"""
    await remove_permission_from_role(db, role_id, permission_id)
    return success_response(message="权限移除成功")

# 用户权限查询
@router.get("/users/{user_id}/permissions")
@require_permissions(["user:read_permissions"])
async def get_user_permissions_route(
    request: Request,
    user_id: int = Path(..., ge=1, description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取用户所有权限"""
    permissions = await get_user_permissions(db, user_id)
    return success_response(data=permissions)