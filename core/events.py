from typing import Callable, List, Dict, Any
from functools import wraps

# 存储启动和关闭时需要执行的函数
startup_handlers: List[Callable] = []
shutdown_handlers: List[Callable] = []

def on_startup(func: Callable) -> Callable:
    """
    注册应用启动时执行的函数装饰器
    
    用法:
    @on_startup
    async def connect_to_db():
        # 连接数据库的代码
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    startup_handlers.append(wrapper)
    return wrapper

def on_shutdown(func: Callable) -> Callable:
    """
    注册应用关闭时执行的函数装饰器
    
    用法:
    @on_shutdown
    async def disconnect_db():
        # 断开数据库连接的代码
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    shutdown_handlers.append(wrapper)
    return wrapper

def register_events(app) -> None:
    """
    将所有事件处理函数注册到 FastAPI 应用
    
    Args:
        app: FastAPI 应用实例
    """
    # 注册启动事件
    for handler in startup_handlers:
        app.add_event_handler("startup", handler)
    
    # 注册关闭事件
    for handler in shutdown_handlers:
        app.add_event_handler("shutdown", handler)
