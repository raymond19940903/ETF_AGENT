"""ETF资产配置策略系统 - 后端主程序"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

# 导入配置和模块
from config.settings import settings
from app.core.database import init_db
from app.cache.redis_client import redis_client
from app.api.auth import router as auth_router
from app.api.conversation import router as conversation_router
from app.api.strategy import router as strategy_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("启动ETF资产配置策略系统...")
    
    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        init_db()
        
        # 连接Redis
        logger.info("连接Redis...")
        await redis_client.connect()
        
        logger.info("系统启动完成")
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("关闭系统...")
    try:
        await redis_client.disconnect()
        logger.info("系统关闭完成")
    except Exception as e:
        logger.error(f"系统关闭异常: {e}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于LangChain和FastAPI的ETF资产配置策略系统",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 添加信任主机中间件
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# 注册路由
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(strategy_router)


@app.get("/", summary="系统信息")
async def root():
    """系统根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "ETF资产配置策略系统运行正常"
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    try:
        # 检查Redis连接
        redis_status = "connected" if redis_client.redis else "disconnected"
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": redis_status,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="系统异常")


@app.get("/api/info", summary="API信息")
async def api_info():
    """API信息接口"""
    return {
        "api_version": "v1",
        "endpoints": [
            "/api/auth/*",
            "/api/conversation/*", 
            "/api/strategy/*"
        ],
        "websocket": "/api/conversation/ws/{session_id}",
        "documentation": "/docs"
    }


# 异常处理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "请求的资源不存在",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"内部服务器错误: {exc}")
    return {
        "error": "Internal Server Error", 
        "message": "服务器内部错误",
        "status_code": 500
    }


if __name__ == "__main__":
    # 运行服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
