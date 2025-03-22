import uvicorn
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from core import debug, info, error, get_db, settings, register_events, api_router

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# 注册事件处理函数
register_events(app)

# 注册主路由（先注册 API 路由）
info("注册主路由")
app.include_router(api_router, prefix="/api")

# 配置静态文件目录（后注册静态文件）
info("配置静态文件目录")
app.mount("/", StaticFiles(directory="web", html=True), name="static")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    # 启动 uvicorn 服务器
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
