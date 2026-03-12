import logging
logger = logging.getLogger(__name__)
"""
平台注册表
Platform Registry

支持动态注册新平台，无需修改核心代码
Supports dynamic registration of new platforms without modifying core code.

使用方式 Usage:
    from app.platforms import PlatformRegistry
    
    # 注册新平台 Register new platform
    PlatformRegistry.register(MyPlatformAdapter)
    
    # 根据URL获取适配器 Get adapter by URL
    adapter = PlatformRegistry.get_adapter(url)
    
    # 列出所有平台 List all platforms
    platforms = PlatformRegistry.list_platforms()
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass

from .base import BasePlatformAdapter, PlatformInfo


@dataclass
class RegisteredPlatform:
    """已注册的平台信息"""
    info: PlatformInfo
    adapter_class: Type[BasePlatformAdapter]


class PlatformRegistry:
    """
    平台注册表
    Platform Registry
    
    单例模式，管理所有平台适配器
    Singleton pattern, manages all platform adapters.
    """
    
    _platforms: Dict[str, RegisteredPlatform] = {}
    _initialized: bool = False
    
    @classmethod
    def register(cls, adapter_class: Type[BasePlatformAdapter]) -> None:
        """
        注册平台适配器
        Register a platform adapter
        
        Args:
            adapter_class: 平台适配器类 Platform adapter class
        
        Example:
            PlatformRegistry.register(ModaoAdapter)
        """
        instance = adapter_class()
        info = instance.info
        
        cls._platforms[info.name] = RegisteredPlatform(
            info=info,
            adapter_class=adapter_class
        )
        
        logger.info(f"[Registry] 注册平台: {info.display_name} ({info.display_name_en})")
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        注销平台适配器
        Unregister a platform adapter
        
        Args:
            name: 平台名称 Platform name
        
        Returns:
            是否注销成功 Whether unregistration was successful
        """
        if name in cls._platforms:
            del cls._platforms[name]
            logger.info(f"[Registry] 注销平台: {name}")
            return True
        return False
    
    @classmethod
    def get_adapter(cls, url: str) -> Optional[BasePlatformAdapter]:
        """
        根据URL获取匹配的适配器
        Get matching adapter by URL
        
        Args:
            url: 待分析的URL URL to analyze
        
        Returns:
            匹配的平台适配器，或None Matching platform adapter, or None
        
        Example:
            adapter = PlatformRegistry.get_adapter("https://modao.cc/xxx")
            if adapter:
                result = await adapter.extract(url)
        """
        for registered in cls._platforms.values():
            instance = registered.adapter_class()
            if instance.match(url):
                return instance
        return None
    
    @classmethod
    def get_adapter_by_name(cls, name: str) -> Optional[BasePlatformAdapter]:
        """
        根据名称获取适配器
        Get adapter by name
        
        Args:
            name: 平台名称 Platform name
        
        Returns:
            平台适配器，或None Platform adapter, or None
        """
        registered = cls._platforms.get(name)
        if registered:
            return registered.adapter_class()
        return None
    
    @classmethod
    def list_platforms(cls) -> List[Dict[str, str]]:
        """
        列出所有已注册的平台
        List all registered platforms
        
        Returns:
            平台信息列表 List of platform information
        
        Example:
            platforms = PlatformRegistry.list_platforms()
            # [{"name": "modao", "display_name": "墨刀", "display_name_en": "Modao"}, ...]
        """
        return [
            {
                "name": r.info.name,
                "display_name": r.info.display_name,
                "display_name_en": r.info.display_name_en,
                "version": r.info.version,
                "author": r.info.author
            }
            for r in cls._platforms.values()
        ]
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """
        检查URL是否被支持
        Check if URL is supported
        
        Args:
            url: 待检查的URL URL to check
        
        Returns:
            是否支持 Whether it's supported
        """
        return cls.get_adapter(url) is not None
    
    @classmethod
    def auto_register(cls) -> None:
        """
        自动注册内置平台
        Auto-register built-in platforms
        
        在模块加载时自动调用
        Automatically called when module is loaded.
        """
        if cls._initialized:
            return
        
        # 注册墨刀平台
        try:
            from app.platforms.modao.adapter import ModaoAdapter
            cls.register(ModaoAdapter)
        except ImportError:
            logger.info("[Registry] 墨刀适配器未找到 / Modao adapter not found")
        
        # 注册蓝湖平台（待实现）
        # try:
        #     from app.platforms.lanhu.adapter import LanhuAdapter
        #     cls.register(LanhuAdapter)
        # except ImportError:
        #     pass
        
        # 注册Figma平台（待实现）
        # try:
        #     from app.platforms.figma.adapter import FigmaAdapter
        #     cls.register(FigmaAdapter)
        # except ImportError:
        #     pass
        
        cls._initialized = True
        logger.info(f"[Registry] 自动注册完成，共 {len(cls._platforms)} 个平台")


# 模块加载时自动注册
PlatformRegistry.auto_register()
