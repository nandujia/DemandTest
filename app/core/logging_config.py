"""
日志配置模块
Logging Configuration

提供统一的日志配置和获取方法
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    配置全局日志
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志文件目录
        log_file: 日志文件名
    """
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        filename = log_file or f"testify_{datetime.now().strftime('%Y%m%d')}.log"
        file_path = log_path / filename
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
    
    Returns:
        配置好的日志器实例
    
    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    return logging.getLogger(name)


# 自动初始化（可被环境变量覆盖）
import os

_log_level = os.getenv("LOG_LEVEL", "INFO")
_log_dir = os.getenv("LOG_DIR", "./logs")

setup_logging(level=_log_level, log_dir=_log_dir)
