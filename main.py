from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
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
    
    # 注册API路由
    app.include_router(api_router, prefix="/api")
    
    # 获取web目录的绝对路径
    web_dir = os.path.join(os.path.dirname(__file__), "web")
    
    # 为静态资源创建路由
    app.mount("/assets", StaticFiles(directory=os.path.join(web_dir, "assets")), name="assets")
    
    # 添加回退路由，处理所有其他请求并返回index.html
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # 如果请求的是API路径，不处理（已由API路由处理）
        if full_path.startswith("api/"):
            return None
            
        # 返回index.html文件
        index_path = os.path.join(web_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"message": "前端文件未找到，请确保web目录中存在index.html"}
    
    info(f"Vue前端应用已配置，支持HTML5 History路由模式")
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
