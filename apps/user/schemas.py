from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

# 角色基础模式
class RoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    name: Optional[str] = Field(None, description="角色名称")

class Role(RoleBase):
    id: int = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 权限基础模式
class PermissionBase(BaseModel):
    code: str = Field(..., description="权限代码")
    name: str = Field(..., description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    code: Optional[str] = Field(None, description="权限代码")
    name: Optional[str] = Field(None, description="权限名称")

class Permission(PermissionBase):
    id: int = Field(..., description="权限ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 用户基础模式
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    phone: Optional[str] = Field(None, description="电话")
    avatar: Optional[str] = Field(None, description="头像")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否超级管理员")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v

    @validator('phone')
    def phone_format(cls, v):
        if v and not re.match(r'^\d{11}$', v):
            raise ValueError('手机号格式不正确')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="密码")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: Optional[str] = Field(None, min_length=6, description="密码")
    full_name: Optional[str] = Field(None, description="全名")
    phone: Optional[str] = Field(None, description="电话")
    avatar: Optional[str] = Field(None, description="头像")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否超级管理员")

    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v

    @validator('phone')
    def phone_format(cls, v):
        if v and not re.match(r'^\d{11}$', v):
            raise ValueError('手机号格式不正确')
        return v

class User(UserBase):
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    roles: List[Role] = Field([], description="用户角色")

    class Config:
        from_attributes = True

# 用户登录模式
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 令牌模式
class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")