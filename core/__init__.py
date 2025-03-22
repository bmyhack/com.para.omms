from .logger import debug, info, error
from .db import get_db
from .config import settings
from .events import register_events
from .api import api_router
# 可以添加 __all__ 来控制 from core import * 的行为
__all__ = ['debug', 'info', 'error', 'get_db', 'settings', 'register_events','api_router']