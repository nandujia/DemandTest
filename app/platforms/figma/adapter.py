"""
Figma平台适配器
Figma Platform Adapter

Figma是流行的在线设计工具
Figma is a popular online design tool.

状态 Status: 开发中 Under Development
注意 Note: Figma使用API而非网络拦截
Warning: Figma uses API instead of network interception
"""

from app.platforms.base import BasePlatformAdapter, PlatformInfo


class FigmaAdapter(BasePlatformAdapter):
    """Figma平台适配器 Figma Platform Adapter"""
    
    @property
    def info(self) -> PlatformInfo:
        return PlatformInfo(
            name="figma",
            display_name="Figma",
            display_name_en="Figma",
            url_patterns=["figma.com"],
            version="0.1.0",
            author="DemandTest Team"
        )
    
    def match(self, url: str) -> bool:
        return "figma.com" in url
    
    def get_sniff_patterns(self) -> dict:
        return {
            "api": ["/api/nodes", "/api/files"],
            "file_data": ["/file/"]
        }
    
    async def parse_sniffed_data(self, sniffed_data):
        # TODO: Figma需要使用官方API
        # Figma requires using official API
        return []