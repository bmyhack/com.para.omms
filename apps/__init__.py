from fastapi import APIRouter
from .user import user_router

# 创建应用路由
apps_router = APIRouter()

# 注册各模块路由
apps_router.include_router(user_router)

# 导出
__all__ = ["apps_router"]