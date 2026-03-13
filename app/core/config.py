"""
应用配置
Application Configuration

使用Pydantic Settings进行配置管理
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "智测AI (Testify AI)"
    APP_VERSION: str = "3.1.0-dev"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    
    # 存储配置
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    DATA_DIR: str = "./data"
    CONFIG_DIR: str = "./data/config"
    SESSION_DIR: str = "./data/sessions"
    
    # 爬虫配置
    CRAWLER_TIMEOUT: int = 60
    CRAWLER_HEADLESS: bool = True
    PAGE_LOAD_TIMEOUT_MS: int = 3000
    PLAYWRIGHT_STORAGE_STATE: Optional[str] = None
    
    # LLM配置
    LLM_API_TYPE: str = "glm"
    LLM_MODEL_NAME: str = "glm-4"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    # 知识库配置
    KB_ENABLED: bool = True
    KB_STORAGE_DIR: str = "./data/knowledge"
    
    # 学习系统配置
    LEARNING_ENABLED: bool = True
    LEARNING_STORAGE_DIR: str = "./data/learning"
    
    # 会话配置
    SESSION_TIMEOUT: int = 3600
    SESSION_MAX_HISTORY: int = 50

    # 账号与鉴权
    AUTH_SECRET_KEY: str = "dev-secret-change-me"
    AUTH_TOKEN_EXPIRE_SECONDS: int = 7 * 24 * 3600
    AUTH_ALLOW_TEST_DEFAULT_PASSWORD: bool = True
    AUTH_TEST_DEFAULT_PASSWORD: str = "123456"
    
    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的CORS源列表"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def get_storage_path(self, storage_type: str) -> Path:
        """获取存储路径"""
        path_map = {
            "upload": self.UPLOAD_DIR,
            "export": self.EXPORT_DIR,
            "data": self.DATA_DIR,
            "config": self.CONFIG_DIR,
            "session": self.SESSION_DIR,
            "log": self.LOG_DIR,
            "knowledge": self.KB_STORAGE_DIR,
            "learning": self.LEARNING_STORAGE_DIR,
        }
        path = Path(path_map.get(storage_type, self.DATA_DIR))
        path.mkdir(parents=True, exist_ok=True)
        return path


# 全局配置实例
settings = Settings()
