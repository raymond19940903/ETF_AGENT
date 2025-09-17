"""
ETF资产配置策略系统 - 配置文件
包含所有外部服务和系统配置信息
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """系统配置类"""
    
    # 应用基本配置
    APP_NAME: str = "ETF资产配置策略系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://username:password@localhost:3306/etf_strategy"
    DATABASE_ECHO: bool = False
    
    # Redis缓存配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # Wind数据库配置
    WIND_DB_HOST: str = "your-wind-server-host"
    WIND_DB_PORT: int = 1433
    WIND_DB_NAME: str = "wind_database"
    WIND_DB_USER: str = "your-wind-username"
    WIND_DB_PASSWORD: str = "your-wind-password"
    WIND_DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    
    @property
    def wind_connection_string(self) -> str:
        """Wind数据库连接字符串"""
        return (
            f"DRIVER={{{self.WIND_DB_DRIVER}}};"
            f"SERVER={self.WIND_DB_HOST},{self.WIND_DB_PORT};"
            f"DATABASE={self.WIND_DB_NAME};"
            f"UID={self.WIND_DB_USER};"
            f"PWD={self.WIND_DB_PASSWORD};"
            "Trusted_Connection=no;"
        )
    
    # 资讯数据接口配置
    NEWS_API_BASE_URL: str = "https://api.example-news.com"
    NEWS_API_KEY: str = "your-news-api-key"
    NEWS_API_TIMEOUT: int = 30
    
    # 财经资讯源配置
    FINANCIAL_NEWS_SOURCES: dict = {
        "sina": {
            "base_url": "https://finance.sina.com.cn/api",
            "timeout": 30,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        },
        "eastmoney": {
            "base_url": "https://api.eastmoney.com",
            "timeout": 30,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
    }
    
    # 本地大模型配置
    LLM_MODEL_TYPE: str = "local"  # local, openai, qwen, etc.
    LLM_MODEL_NAME: str = "qwen2-7b"
    LLM_MODEL_PATH: str = "/path/to/your/local/model"
    LLM_API_BASE: str = "http://localhost:11434"  # Ollama默认地址
    LLM_API_KEY: Optional[str] = None
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT: int = 60
    
    # OpenAI配置（备用）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Celery任务队列配置
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    CELERY_ENABLE_UTC: bool = True
    
    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 缓存配置
    CACHE_TTL_DEFAULT: int = 3600  # 1小时
    CACHE_TTL_USER_SESSION: int = 30 * 24 * 3600  # 30天
    CACHE_TTL_ETF_DATA: int = 5 * 60  # 5分钟
    CACHE_TTL_STRATEGY: int = 30 * 60  # 30分钟
    CACHE_TTL_NEWS: int = 30 * 60  # 30分钟
    CACHE_TTL_CONVERSATION: int = 2 * 3600  # 2小时
    
    # 业务配置
    MAX_CONVERSATION_ROUNDS: int = 10
    MAX_STRATEGY_HISTORY: int = 50
    DEFAULT_BACKTEST_PERIOD: int = 365  # 天
    MAX_ETF_COUNT_PER_STRATEGY: int = 20
    
    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: set = {".pdf", ".doc", ".docx", ".txt"}
    
    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


# 开发环境配置
class DevelopmentSettings(Settings):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_ECHO: bool = True


# 生产环境配置
class ProductionSettings(Settings):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_ECHO: bool = False
    
    # 生产环境安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")


def get_settings() -> Settings:
    """根据环境变量获取配置"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()
