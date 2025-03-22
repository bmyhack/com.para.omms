from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from fastapi import Depends
from .logger import debug, info, error
from .config import settings
from .events import on_startup, on_shutdown
from sqlalchemy.ext.declarative import declarative_base
import importlib
import pkgutil
import os

# 数据库连接配置
engine = None
AsyncSessionLocal = None

async def init_db():
    """初始化数据库引擎和会话工厂"""
    global engine, AsyncSessionLocal
    try:
        # 使用异步引擎，URL格式：postgresql+asyncpg://user:password@host:port/dbname
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        info("数据库引擎创建成功")
        # 创建异步会话工厂
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        return True
    except Exception as e:
        error(f"数据库引擎创建失败: {e}")
        raise

# 异步上下文管理器用于管理会话
@asynccontextmanager
async def get_db_session():
    session = AsyncSessionLocal()
    info("数据库会话已创建")
    try:
        yield session
        await session.commit()
        info("数据库事务已提交")
    except Exception as e:
        await session.rollback()
        error(f"数据库事务回滚: {e}")
        raise e
    finally:
        await session.close()
        info("数据库会话已关闭")

# 依赖注入函数
async def get_db() -> AsyncSession:
    async with get_db_session() as session:
        yield session

Base = declarative_base()

def load_all_models():
    """动态加载所有模型"""
    apps_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apps')
    for app in pkgutil.iter_modules([apps_dir]):
        if not app.ispkg:
            continue
        try:
            models_module = importlib.import_module(f'apps.{app.name}.models')
            info(f"已加载模型: apps.{app.name}.models")
        except ImportError:
            continue

@on_startup
async def verify_database_connection():
    """应用启动时验证数据库连接并确保表存在"""
    await init_db()
    info("正在验证数据库连接...")
    try:
        # 加载所有模型
        load_all_models()
        
        # 创建所有表
        async with engine.begin() as conn:
            info("正在检查并创建数据库表...")
            await conn.run_sync(Base.metadata.create_all)
            info("数据库表创建/更新完成")
        
        # 验证连接
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            info("数据库连接验证成功")
    except Exception as e:
        error(f"数据库初始化失败: {e}")
        raise

@on_shutdown
async def close_database_connections():
    """应用关闭时关闭所有数据库连接"""
    info("正在关闭数据库连接池...")
    if engine:
        await engine.dispose()
        info("数据库连接池已关闭")
