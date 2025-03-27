from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from fastapi import Depends
from .logger import debug, info, error
from .config import settings
from .events import on_startup, on_shutdown
import importlib
import pkgutil
import os

# 数据库连接配置
engine = None
SessionLocal = None
Base = declarative_base()

def init_db():
    """初始化数据库引擎和会话工厂"""
    global engine, SessionLocal
    try:
        # 使用同步引擎，URL格式：mysql+pymysql://user:password@host:port/dbname
        engine = create_engine(
            settings.DATABASE_URL.replace('mysql+aiomysql', 'mysql+pymysql'), 
            echo=settings.DB_ECHO,  # 修改这里：DB_ECHO -> echo
            pool_size=10,  # 连接池大小
            max_overflow=20,  # 超过连接池大小外最多创建的连接
            pool_recycle=3600,  # 连接回收时间，避免MySQL的wait_timeout断开连接
            pool_pre_ping=True  # 连接前ping一下，确保连接有效
        )
        info("数据库引擎创建成功")
        # 创建同步会话工厂
        SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=engine
        )
        return True
    except Exception as e:
        error(f"数据库引擎创建失败: {e}")
        raise

# 同步上下文管理器用于管理会话
@contextmanager
def get_db_context():
    """获取数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """获取数据库会话的依赖项函数"""
    with get_db_context() as session:
        yield session

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
def verify_database_connection():
    """应用启动时验证数据库连接并确保表存在"""
    init_db()
    info("正在验证数据库连接...")
    try:
        # 加载所有模型
        load_all_models()
        
        # 创建所有表
        with engine.begin() as conn:
            info("正在检查并创建数据库表...")
            # 为MySQL设置字符集和引擎
            conn.execute(text("SET NAMES utf8mb4"))
            conn.execute(text("SET CHARACTER SET utf8mb4"))
            Base.metadata.create_all(bind=engine)
            info("数据库表创建/更新完成")
        
        # 验证连接
        with get_db_context() as session:
            session.execute(text("SELECT 1"))
            info("数据库连接验证成功")
    except Exception as e:
        error(f"数据库初始化失败: {e}")
        raise

@on_shutdown
def close_database_connections():
    """应用关闭时关闭所有数据库连接"""
    info("正在关闭数据库连接池...")
    if engine:
        engine.dispose()
        info("数据库连接池已关闭")
