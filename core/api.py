from fastapi import APIRouter

# 创建主路由
api_router = APIRouter()

# 导入各模块路由
# from apps.user import user_router
# from apps.monitor import monitor_router
# 注册各模块路由
# api_router.include_router(user_router, prefix="/v1", tags=["用户认证与管理"])
# api_router.include_router(monitor_router, prefix="/v1", tags=["监控管理"])

# 这里可以继续注册其他模块的路由
# 例如:
# from apps.some_module import some_router
# api_router.include_router(some_router, prefix="/some-prefix", tags=["Some Tag"])

