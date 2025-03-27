from typing import Callable, List
import inspect
from .logger import info

# 启动事件处理器列表
startup_handlers: List[Callable] = []
# 关闭事件处理器列表
shutdown_handlers: List[Callable] = []

def on_startup(func: Callable) -> Callable:
    """
    应用启动时执行的函数装饰器
    """
    startup_handlers.append(func)
    
    # 检查是否为异步函数
    if inspect.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
    else:
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
    return wrapper

def on_shutdown(func: Callable) -> Callable:
    """
    应用关闭时执行的函数装饰器
    """
    shutdown_handlers.append(func)
    
    # 检查是否为异步函数
    if inspect.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
    else:
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
    
    return wrapper

async def run_startup_handlers():
    """运行所有启动处理器"""
    for handler in startup_handlers:
        if inspect.iscoroutinefunction(handler):
            await handler()
        else:
            handler()

async def run_shutdown_handlers():
    """运行所有关闭处理器"""
    for handler in shutdown_handlers:
        if inspect.iscoroutinefunction(handler):
            await handler()
        else:
            handler()

def register_events(app):
    """
    注册应用事件处理器
    
    Args:
        app: FastAPI 应用实例
    """
    @app.on_event("startup")
    async def startup():
        info("启动装饰器")
        await run_startup_handlers()
    
    @app.on_event("shutdown")
    async def shutdown():
        info("关闭装饰器")
        await run_shutdown_handlers()
