"""
配置文件
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "DemandTest Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 爬虫配置
    CRAWLER_TIMEOUT: int = 60
    CRAWLER_HEADLESS: bool = True
    
    # 文件存储
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    
    # OCR 配置
    OCR_API_KEY: str = "K81996634488957"
    OCR_API_URL: str = "https://api.ocr.space/parse/image"
    
    class Config:
        env_file = ".env"


settings = Settings()
