from pydantic_settings import BaseSettings
from .logger import debug, info, error
from dotenv import load_dotenv
import os

# 默认配置
DEFAULT_CONFIG = {
    "APP_NAME": "OMMS",
    "APP_DESCRIPTION": "Operations Management and Monitoring System",
    "APP_VERSION": "1.0.0",
    "APP_DEBUG": "False",
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "3306",  
    "DATABASE_USER": "omms",
    "DATABASE_PASSWORD": "omms",
    "DATABASE_NAME": "omms",
    "DB_ECHO": "True"
}

# 加载环境变量
dotenv_loaded = load_dotenv()
if not dotenv_loaded:
    error("警告：.env 文件未成功加载，将使用默认配置")
    # 设置默认环境变量
    for key, value in DEFAULT_CONFIG.items():
        if not os.getenv(key):
            os.environ[key] = value
    info("已加载默认配置")
else:
    info("加载 .env 文件成功")

# 打印配置信息
error("----------------------------------------------------------------")
debug("当前配置信息：")
debug(f"APP_NAME: {os.getenv('APP_NAME', DEFAULT_CONFIG['APP_NAME'])}")
debug(f"APP_DESCRIPTION: {os.getenv('APP_DESCRIPTION', DEFAULT_CONFIG['APP_DESCRIPTION'])}")
debug(f"APP_VERSION: {os.getenv('APP_VERSION', DEFAULT_CONFIG['APP_VERSION'])}")
debug(f"APP_DEBUG: {os.getenv('APP_DEBUG', DEFAULT_CONFIG['APP_DEBUG'])}")
debug(f"DATABASE_HOST: {os.getenv('DATABASE_HOST', DEFAULT_CONFIG['DATABASE_HOST'])}")
debug(f"DATABASE_PORT: {os.getenv('DATABASE_PORT', DEFAULT_CONFIG['DATABASE_PORT'])}")
debug(f"DATABASE_USER: {os.getenv('DATABASE_USER', DEFAULT_CONFIG['DATABASE_USER'])}")
debug(f"DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD', DEFAULT_CONFIG['DATABASE_PASSWORD'])}")
debug(f"DATABASE_NAME: {os.getenv('DATABASE_NAME', DEFAULT_CONFIG['DATABASE_NAME'])}")
error("----------------------------------------------------------------")
class Settings(BaseSettings):
    # 应用相关配置
    APP_NAME: str = os.getenv("APP_NAME", DEFAULT_CONFIG["APP_NAME"])
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", DEFAULT_CONFIG["APP_DESCRIPTION"])
    APP_VERSION: str = os.getenv("APP_VERSION", DEFAULT_CONFIG["APP_VERSION"])
    APP_DEBUG: bool = os.getenv("APP_DEBUG", DEFAULT_CONFIG["APP_DEBUG"]).lower() == "true"

    # 数据库相关配置
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", DEFAULT_CONFIG["DATABASE_HOST"])
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", DEFAULT_CONFIG["DATABASE_PORT"]))
    DATABASE_USER: str = os.getenv("DATABASE_USER", DEFAULT_CONFIG["DATABASE_USER"])
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", DEFAULT_CONFIG["DATABASE_PASSWORD"])
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", DEFAULT_CONFIG["DATABASE_NAME"])
    DB_ECHO: bool = os.getenv("DB_ECHO", DEFAULT_CONFIG["DB_ECHO"]).lower() == "true"
    DATABASE_URL: str = "mysql+aiomysql://{user}:{password}@{host}:{port}/{db}".format(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        db=DATABASE_NAME,
    )
    
    # 添加 JWT 密钥
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pqev3YhW8N5ivq8tlPJk7Q")
    # Prometheus配置
    PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://10.249.61.3:9090")
    class Config:
        case_sensitive = True

# 创建单例实例
settings = Settings()
