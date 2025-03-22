from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from jose import jwt

from core.config import settings
from core.exceptions import NotFoundError, BusinessError, AuthenticationError
from .models import User, Role, Permission, user_role, role_permission
from .schemas import UserCreate, UserUpdate, RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 用户服务
async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """获取用户信息"""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.username == username)
    )
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """通过邮箱获取用户"""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.email == email)
    )
    return result.scalars().first()

async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    filters: Dict[str, Any] = None
) -> List[User]:
    """获取用户列表"""
    query = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)
    
    # 应用过滤条件
    if filters:
        if filters.get("username"):
            query = query.where(User.username.ilike(f"%{filters['username']}%"))
        if filters.get("email"):
            query = query.where(User.email.ilike(f"%{filters['email']}%"))
        if filters.get("is_active") is not None:
            query = query.where(User.is_active == filters["is_active"])
        if filters.get("is_superuser") is not None:
            query = query.where(User.is_superuser == filters["is_superuser"])
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise BusinessError("用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = await get_user_by_email(db, user_in.email)
    if existing_email:
        raise BusinessError("邮箱已存在")
    
    # 创建用户对象
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=pwd_context.hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        avatar=user_in.avatar,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    # 获取用户
    db_user = await get_user(db, user_id)
    if not db_user:
        raise NotFoundError("用户不存在")
    
    # 准备更新数据
    update_data = user_in.dict(exclude_unset=True)
    
    # 如果更新用户名，检查是否已存在
    if "username" in update_data and update_data["username"] != db_user.username:
        existing_user = await get_user_by_username(db, update_data["username"])
        if existing_user:
            raise BusinessError("用户名已存在")
    
    # 如果更新邮箱，检查是否已存在
    if "email" in update_data and update_data["email"] != db_user.email:
        existing_email = await get_user_by_email(db, update_data["email"])
        if existing_email:
            raise BusinessError("邮箱已存在")
    
    # 如果更新密码，需要加密
    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
    
    # 执行更新
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """删除用户"""
    db_user = await get_user(db, user_id)
    if not db_user:
        raise NotFoundError("用户不存在")
    
    await db.delete(db_user)
    await db.commit()
    return True

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def update_last_login(db: AsyncSession, user_id: int) -> None:
    """更新最后登录时间"""
    await db.execute(
        update(User).where(User.id == user_id).values(last_login=datetime.utcnow())
    )
    await db.commit()

# 角色服务
async def get_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    """获取角色信息"""
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    return result.scalars().first()

async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    """通过名称获取角色"""
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.name == name)
    )
    return result.scalars().first()

async def get_roles(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    name: Optional[str] = None
) -> List[Role]:
    """获取角色列表"""
    query = select(Role).options(selectinload(Role.permissions)).offset(skip).limit(limit)
    
    if name:
        query = query.where(Role.name.ilike(f"%{name}%"))
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_role(db: AsyncSession, role_in: RoleCreate) -> Role:
    """创建角色"""
    # 检查角色名是否已存在
    existing_role = await get_role_by_name(db, role_in.name)
    if existing_role:
        raise BusinessError("角色名已存在")
    
    # 创建角色对象
    db_role = Role(
        name=role_in.name,
        description=role_in.description
    )
    
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def update_role(db: AsyncSession, role_id: int, role_in: RoleUpdate) -> Optional[Role]:
    """更新角色信息"""
    # 获取角色
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    # 准备更新数据
    update_data = role_in.dict(exclude_unset=True)
    
    # 如果更新角色名，检查是否已存在
    if "name" in update_data and update_data["name"] != db_role.name:
        existing_role = await get_role_by_name(db, update_data["name"])
        if existing_role:
            raise BusinessError("角色名已存在")
    
    # 执行更新
    for key, value in update_data.items():
        setattr(db_role, key, value)
    
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def delete_role(db: AsyncSession, role_id: int) -> bool:
    """删除角色"""
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    await db.delete(db_role)
    await db.commit()
    return True

async def assign_role_to_user(db: AsyncSession, user_id: int, role_id: int) -> bool:
    """为用户分配角色"""
    # 检查用户是否存在
    db_user = await get_user(db, user_id)
    if not db_user:
        raise NotFoundError("用户不存在")
    
    # 检查角色是否存在
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    # 检查是否已分配
    if db_role in db_user.roles:
        return True
    
    # 分配角色
    db_user.roles.append(db_role)
    await db.commit()
    return True

async def remove_role_from_user(db: AsyncSession, user_id: int, role_id: int) -> bool:
    """从用户移除角色"""
    # 检查用户是否存在
    db_user = await get_user(db, user_id)
    if not db_user:
        raise NotFoundError("用户不存在")
    
    # 检查角色是否存在
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    # 检查是否已分配
    if db_role not in db_user.roles:
        return True
    
    # 移除角色
    db_user.roles.remove(db_role)
    await db.commit()
    return True

# 权限服务
async def get_permission(db: AsyncSession, permission_id: int) -> Optional[Permission]:
    """获取权限信息"""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    return result.scalars().first()

async def get_permission_by_code(db: AsyncSession, code: str) -> Optional[Permission]:
    """通过代码获取权限"""
    result = await db.execute(
        select(Permission).where(Permission.code == code)
    )
    return result.scalars().first()

async def get_permissions(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    code: Optional[str] = None,
    name: Optional[str] = None
) -> List[Permission]:
    """获取权限列表"""
    query = select(Permission).offset(skip).limit(limit)
    
    if code:
        query = query.where(Permission.code.ilike(f"%{code}%"))
    if name:
        query = query.where(Permission.name.ilike(f"%{name}%"))
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_permission(db: AsyncSession, permission_in: PermissionCreate) -> Permission:
    """创建权限"""
    # 检查权限代码是否已存在
    existing_permission = await get_permission_by_code(db, permission_in.code)
    if existing_permission:
        raise BusinessError("权限代码已存在")
    
    # 创建权限对象
    db_permission = Permission(
        code=permission_in.code,
        name=permission_in.name,
        description=permission_in.description
    )
    
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

async def update_permission(db: AsyncSession, permission_id: int, permission_in: PermissionUpdate) -> Optional[Permission]:
    """更新权限信息"""
    # 获取权限
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise NotFoundError("权限不存在")
    
    # 准备更新数据
    update_data = permission_in.dict(exclude_unset=True)
    
    # 如果更新权限代码，检查是否已存在
    if "code" in update_data and update_data["code"] != db_permission.code:
        existing_permission = await get_permission_by_code(db, update_data["code"])
        if existing_permission:
            raise BusinessError("权限代码已存在")
    
    # 执行更新
    for key, value in update_data.items():
        setattr(db_permission, key, value)
    
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

async def delete_permission(db: AsyncSession, permission_id: int) -> bool:
    """删除权限"""
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise NotFoundError("权限不存在")
    
    await db.delete(db_permission)
    await db.commit()
    return True

async def assign_permission_to_role(db: AsyncSession, role_id: int, permission_id: int) -> bool:
    """为角色分配权限"""
    # 检查角色是否存在
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    # 检查权限是否存在
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise NotFoundError("权限不存在")
    
    # 检查是否已分配
    if db_permission in db_role.permissions:
        return True
    
    # 分配权限
    db_role.permissions.append(db_permission)
    await db.commit()
    return True

async def remove_permission_from_role(db: AsyncSession, role_id: int, permission_id: int) -> bool:
    """从角色移除权限"""
    # 检查角色是否存在
    db_role = await get_role(db, role_id)
    if not db_role:
        raise NotFoundError("角色不存在")
    
    # 检查权限是否存在
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise NotFoundError("权限不存在")
    
    # 检查是否已分配
    if db_permission not in db_role.permissions:
        return True
    
    # 移除权限
    db_role.permissions.remove(db_permission)
    await db.commit()
    return True

async def get_user_permissions(db: AsyncSession, user_id: int) -> List[str]:
    """获取用户所有权限代码"""
    # 获取用户及其角色
    db_user = await get_user(db, user_id)
    if not db_user:
        raise NotFoundError("用户不存在")
    
    # 如果是超级管理员，返回所有权限
    if db_user.is_superuser:
        result = await db.execute(select(Permission.code))
        return [code for (code,) in result]
    
    # 获取用户所有角色的权限
    permission_codes = set()
    for role in db_user.roles:
        for permission in role.permissions:
            permission_codes.add(permission.code)
    
    return list(permission_codes)