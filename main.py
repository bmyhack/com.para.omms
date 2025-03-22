from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import (
    settings, register_events, api_router, 
    register_exception_handlers, APIResponse
)
from core.logger import info

def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用
    
    Returns:
        配置好的 FastAPI 应用实例
    """
    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        # 使用自定义响应类
        default_response_class=APIResponse
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该限制为特定域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 注册事件处理器
    register_events(app)
    
    # 注册路由
    app.include_router(api_router, prefix="/api")
    
    # 添加根路由
    @app.get("/")
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "message": "欢迎使用 OMMS API"
        }
    
    info(f"{settings.APP_NAME} 应用已创建")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG
    )
