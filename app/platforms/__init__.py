"""
平台插件模块
Platform Plugin Module

每个平台一个插件目录，实现低侵入式数据提取
Each platform has its own plugin directory for non-intrusive data extraction.
"""

from .base import BasePlatformAdapter
from .registry import PlatformRegistry

__all__ = [
    "BasePlatformAdapter",
    "PlatformRegistry",
]
