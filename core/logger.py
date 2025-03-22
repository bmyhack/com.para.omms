import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Union, List

from loguru import logger

class LogConfig:
    """日志配置类"""
    
    def __init__(
        self,
        log_file: str = "./logs/app-{time:YYYY-MM-DD}.log",
        log_level: str = "DEBUG",
        rotation: str = "500 MB",
        retention: str = "7 days",
        format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        intercept_loggers: List[str] = ["uvicorn", "uvicorn.access"]
    ):
        self.log_file = log_file
        self.log_level = log_level
        self.rotation = rotation
        self.retention = retention
        self.format = format
        self.intercept_loggers = intercept_loggers

class InterceptHandler(logging.Handler):
    """自定义日志处理器，将标准日志转发到 loguru"""
    
    def emit(self, record):
        # 获取对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 使用 loguru 记录日志
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

class Logger:
    """日志管理类"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[LogConfig] = None):
        if not hasattr(self, 'initialized'):
            self.config = config or LogConfig()
            self.setup_logging()
            self.initialized = True
    
    def setup_logging(self):
        """配置日志系统"""
        # 移除所有默认处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            format=self.config.format,
            level=self.config.log_level,
            colorize=True
        )
        
        # 添加文件输出
        logger.add(
            self.config.log_file,
            rotation=self.config.rotation,
            retention=self.config.retention,
            level=self.config.log_level,
            format=self.config.format
        )
        
        # 拦截其他日志库
        self.intercept_standard_loggers()
    
    def intercept_standard_loggers(self):
        """拦截标准日志库的日志"""
        for logger_name in self.config.intercept_loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler()]
            logging_logger.propagate = False
    
    @property
    def log(self):
        """获取 logger 实例"""
        return logger

# 创建默认日志实例
default_logger = Logger().log

# 导出常用日志方法，方便直接调用
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception
