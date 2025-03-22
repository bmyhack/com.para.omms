from fastapi import APIRouter
from .routes import router
from core.events import on_startup
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db_session
from .models import User, Role, Permission
from .services import get_user_by_username, create_user, get_role_by_name, create_role, get_permission_by_code, create_permission
from .schemas import UserCreate, RoleCreate, PermissionCreate
from sqlalchemy.orm import selectinload
from sqlalchemy import select

# 创建用户模块路由
user_router = APIRouter()
user_router.include_router(router, prefix="/auth", tags=["用户认证与管理"])

# 初始化数据
@on_startup
async def init_user_data():
    """
    初始化用户模块数据
    - 创建默认超级管理员
    - 创建默认角色
    - 创建默认权限
    """
    async with get_db_session() as db:
        # 创建超级管理员
        await init_superuser(db)
        
        # 创建默认角色
        admin_role_id = await init_roles(db)
        
        # 创建默认权限
        permissions = await init_permissions(db)
        
        # 为管理员角色分配所有权限
        if admin_role_id and permissions:
            await assign_permissions_to_admin(db, admin_role_id, permissions)

async def init_superuser(db: AsyncSession):
    """创建超级管理员账户"""
    # 检查超级管理员是否已存在
    admin = await get_user_by_username(db, "admin")
    if not admin:
        # 创建超级管理员
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="Admin@123",
            is_active=True,
            is_superuser=True
        )
        await create_user(db, admin_data)
        print("已创建超级管理员账户")

async def init_roles(db: AsyncSession):
    """创建默认角色"""
    # 检查管理员角色是否已存在
    admin_role = await get_role_by_name(db, "管理员")
    if not admin_role:
        # 创建管理员角色
        role_data = RoleCreate(
            name="管理员",
            description="系统管理员，拥有所有权限"
        )
        admin_role = await create_role(db, role_data)
        print("已创建管理员角色")
    
    # 检查普通用户角色是否已存在
    user_role = await get_role_by_name(db, "普通用户")
    if not user_role:
        # 创建普通用户角色
        role_data = RoleCreate(
            name="普通用户",
            description="普通用户，拥有基本权限"
        )
        await create_role(db, role_data)
        print("已创建普通用户角色")
    
    return admin_role.id if admin_role else None

async def init_permissions(db: AsyncSession):
    """创建默认权限"""
    permissions = []
    
    # 用户管理权限
    user_permissions = [
        {"code": "user:list", "name": "用户列表", "description": "查看用户列表"},
        {"code": "user:read", "name": "用户详情", "description": "查看用户详情"},
        {"code": "user:create", "name": "创建用户", "description": "创建新用户"},
        {"code": "user:update", "name": "更新用户", "description": "更新用户信息"},
        {"code": "user:delete", "name": "删除用户", "description": "删除用户"},
        {"code": "user:assign_role", "name": "分配角色", "description": "为用户分配角色"},
        {"code": "user:remove_role", "name": "移除角色", "description": "从用户移除角色"},
        {"code": "user:read_permissions", "name": "查看权限", "description": "查看用户权限"}
    ]
    
    # 角色管理权限
    role_permissions = [
        {"code": "role:list", "name": "角色列表", "description": "查看角色列表"},
        {"code": "role:read", "name": "角色详情", "description": "查看角色详情"},
        {"code": "role:create", "name": "创建角色", "description": "创建新角色"},
        {"code": "role:update", "name": "更新角色", "description": "更新角色信息"},
        {"code": "role:delete", "name": "删除角色", "description": "删除角色"},
        {"code": "role:assign_permission", "name": "分配权限", "description": "为角色分配权限"},
        {"code": "role:remove_permission", "name": "移除权限", "description": "从角色移除权限"}
    ]
    
    # 权限管理权限
    permission_permissions = [
        {"code": "permission:list", "name": "权限列表", "description": "查看权限列表"},
        {"code": "permission:read", "name": "权限详情", "description": "查看权限详情"},
        {"code": "permission:create", "name": "创建权限", "description": "创建新权限"},
        {"code": "permission:update", "name": "更新权限", "description": "更新权限信息"},
        {"code": "permission:delete", "name": "删除权限", "description": "删除权限"}
    ]
    
    # 合并所有权限
    all_permissions = user_permissions + role_permissions + permission_permissions
    
    # 创建权限
    for perm_data in all_permissions:
        # 检查权限是否已存在
        permission = await get_permission_by_code(db, perm_data["code"])
        if not permission:
            # 创建权限
            permission_data = PermissionCreate(
                code=perm_data["code"],
                name=perm_data["name"],
                description=perm_data["description"]
            )
            permission = await create_permission(db, permission_data)
            print(f"已创建权限: {perm_data['name']}")
        
        permissions.append(permission)
    
    return permissions

async def assign_permissions_to_admin(db: AsyncSession, role_id: int, permissions: list):
    """为管理员角色分配所有权限"""
    # 显式加载角色及其权限
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    admin_role = result.scalars().first()
    
    if not admin_role:
        return
    
    # 获取当前角色已有的权限代码
    existing_permission_codes = {p.code for p in admin_role.permissions}
    
    # 添加新权限
    for permission in permissions:
        if permission.code not in existing_permission_codes:
            admin_role.permissions.append(permission)
            print(f"为管理员角色添加权限: {permission.name}")
    
    await db.commit()
    print("管理员角色权限更新完成")

# 导出模块
__all__ = ["user_router"]