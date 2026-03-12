import logging
logger = logging.getLogger(__name__)
"""
平台适配器基类
Platform Adapter Base Class

设计原则 Design Principles:
1. 低侵入 (Non-intrusive): 不依赖DOM/OCR，只做数据嗅探
2. 可插拔 (Pluggable): 新平台只需实现parse_data方法
3. 标准化输出 (Standardized Output): 统一转换为RequirementNode
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.core.schema import RequirementNode, ExtractionResult
from app.adapters.sniffer import DataSniffer, SniffedData


@dataclass
class PlatformInfo:
    """平台信息 Platform Information"""
    name: str                    # 平台标识 Platform identifier
    display_name: str            # 显示名称 Display name (中文)
    display_name_en: str         # 英文名称 English name
    url_patterns: List[str]      # URL匹配模式 URL patterns
    version: str = "1.0.0"       # 适配器版本 Adapter version
    author: str = ""             # 作者 Author


class BasePlatformAdapter(ABC):
    """
    平台适配器抽象基类
    Abstract Base Class for Platform Adapters
    
    子类必须实现的方法 Methods that subclasses must implement:
    - get_platform_info(): 返回平台信息
    - get_sniff_patterns(): 返回数据嗅探模式
    - parse_sniffed_data(): 解析嗅探到的数据
    """
    
    def __init__(self):
        self.sniffer = DataSniffer()
        self._cached_data: List[SniffedData] = []
    
    @property
    @abstractmethod
    def info(self) -> PlatformInfo:
        """返回平台信息 Return platform information"""
        pass
    
    @abstractmethod
    def match(self, url: str) -> bool:
        """
        判断URL是否匹配此平台
        Check if URL matches this platform
        
        Args:
            url: 待检查的URL URL to check
        
        Returns:
            是否匹配 Whether it matches
        """
        pass
    
    @abstractmethod
    def get_sniff_patterns(self) -> Dict[str, List[str]]:
        """
        获取数据嗅探模式
        Get data sniffing patterns
        
        Returns:
            嗅探模式字典，如:
            {
                "document_js": ["document.js"],
                "api": ["/api/pages", "/api/workspace"],
                "sitemap": ["sitemap", "treelist"]
            }
        """
        pass
    
    @abstractmethod
    async def parse_sniffed_data(
        self,
        sniffed_data: List[SniffedData]
    ) -> List[RequirementNode]:
        """
        解析嗅探到的数据
        Parse sniffed data
        
        这是最关键的方法：将原始JSON转换为标准需求节点
        This is the most critical method: convert raw JSON to standardized requirement nodes.
        
        Args:
            sniffed_data: 嗅探到的数据列表 List of sniffed data
        
        Returns:
            标准化的需求节点列表 List of standardized requirement nodes
        """
        pass
    
    async def extract(self, url: str) -> ExtractionResult:
        """
        执行提取流程
        Execute extraction workflow
        
        标准流程 Standard Workflow:
        1. 设置嗅探模式 Set up sniffing patterns
        2. 执行嗅探 Execute sniffing
        3. 解析数据 Parse data
        4. 返回结果 Return result
        """
        start_time = datetime.now()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[{self.info.display_name}] 开始数据提取")
        logger.info(f"[{self.info.display_name_en}] Starting data extraction")
        logger.info(f"URL: {url}")
        logger.info(f"{'='*60}\n")
        
        try:
            # Step 1: 设置嗅探模式
            patterns = self.get_sniff_patterns()
            self.sniffer.patterns = {}
            
            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    self.sniffer.register_pattern(category, pattern)
            
            logger.info(f"[INFO] 已注册 {len(self.sniffer.patterns)} 个嗅探模式")
            logger.info(f"[INFO] Registered {len(self.sniffer.patterns)} sniffing patterns")
            
            # Step 2: 执行嗅探
            sniff_result = await self.sniffer.sniff(url, platform=self.info.name)
            
            # Step 3: 重建SniffedData对象
            self._cached_data = []
            for source, items in sniff_result.get("data_sources", {}).items():
                for item in items:
                    self._cached_data.append(SniffedData(
                        url=item["url"],
                        method="GET",
                        status=item["status"],
                        headers={},
                        body=item.get("body"),
                        source=source,
                        parsed=item.get("parsed")
                    ))
            
            # Step 4: 解析数据
            if sniff_result.get("sniffed_count", 0) > 0:
                nodes = await self.parse_sniffed_data(self._cached_data)
            else:
                nodes = []
                logger.info(f"[WARN] 未拦截到任何数据包")
                logger.info(f"[WARN] No data packets intercepted")
            
            # Step 5: 返回结果
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[SUCCESS] 提取完成")
            logger.info(f"  页面数: {len(nodes)}")
            logger.info(f"  耗时: {elapsed:.2f}秒")
            logger.info(f"{'='*60}\n")
            
            return ExtractionResult(
                platform=self.info.name,
                url=url,
                pages=nodes,
                total_elements=sum(len(n.elements) for n in nodes),
                success=len(nodes) > 0,
                error=None if nodes else "未提取到数据 / No data extracted"
            )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[ERROR] 提取失败")
            logger.info(f"  错误: {e}")
            logger.info(f"  耗时: {elapsed:.2f}秒")
            logger.info(f"{'='*60}\n")
            
            return ExtractionResult(
                platform=self.info.name,
                url=url,
                pages=[],
                success=False,
                error=str(e)
            )
    
    def get_cached_data(self) -> List[SniffedData]:
        """获取缓存的嗅探数据 Get cached sniffed data"""
        return self._cached_data
