"""
墨刀平台适配器
Modao Platform Adapter

墨刀是国产原型设计工具，类似Axure
Modao is a Chinese prototyping tool, similar to Axure.

数据提取策略 Data Extraction Strategy:
1. 拦截document.js获取页面结构
2. 拦截API获取组件数据
3. 解析JSON转换为标准格式
"""

import re
import json
from typing import Dict, List, Any, Optional

from app.platforms.base import BasePlatformAdapter, PlatformInfo
from app.core.schema import RequirementNode, UIElement, ElementType
from app.adapters.sniffer import SniffedData


class ModaoAdapter(BasePlatformAdapter):
    """墨刀平台适配器 Modao Platform Adapter"""
    
    @property
    def info(self) -> PlatformInfo:
        return PlatformInfo(
            name="modao",
            display_name="墨刀",
            display_name_en="Modao",
            url_patterns=["modao.cc", "modao.com"],
            version="1.0.0",
            author="DemandTest Team"
        )
    
    def match(self, url: str) -> bool:
        """检查URL是否为墨刀平台"""
        return any(pattern in url for pattern in self.info.url_patterns)
    
    def get_sniff_patterns(self) -> Dict[str, List[str]]:
        """
        获取墨刀的数据嗅探模式
        Get Modao data sniffing patterns
        
        关键数据接口 Key Data Interfaces:
        - document.js: 页面结构和组件数据
        - /api/pages: 页面列表
        - sitemap: 站点地图
        """
        return {
            # 文档数据
            "document_js": [
                "document.js",
                "document.min.js"
            ],
            # API接口
            "api": [
                "/api/pages",
                "/api/workspace",
                "/api/project",
                "/api/design",
            ],
            # 站点地图
            "sitemap": [
                "sitemap",
                "treelist",
                "pagelist"
            ],
            # Axure数据
            "axdata": [
                "axdata.modao",
                "start.html",
                "vip.html"
            ]
        }
    
    async def parse_sniffed_data(
        self,
        sniffed_data: List[SniffedData]
    ) -> List[RequirementNode]:
        """
        解析墨刀的嗅探数据
        Parse Modao sniffed data
        
        解析策略 Parsing Strategy:
        1. 优先解析document.js中的页面结构
        2. 解析API返回的JSON数据
        3. 合并去重
        """
        nodes = []
        seen_page_ids = set()
        
        for data in sniffed_data:
            if data.source == "document_js":
                # 解析document.js
                parsed_nodes = await self._parse_document_js(data)
                for node in parsed_nodes:
                    if node.page_id not in seen_page_ids:
                        nodes.append(node)
                        seen_page_ids.add(node.page_id)
            
            elif data.source == "api":
                # 解析API数据
                parsed_nodes = await self._parse_api_data(data)
                for node in parsed_nodes:
                    if node.page_id not in seen_page_ids:
                        nodes.append(node)
                        seen_page_ids.add(node.page_id)
            
            elif data.source == "sitemap":
                # 解析站点地图
                parsed_nodes = await self._parse_sitemap(data)
                for node in parsed_nodes:
                    if node.page_id not in seen_page_ids:
                        nodes.append(node)
                        seen_page_ids.add(node.page_id)
        
        return nodes
    
    async def _parse_document_js(self, data: SniffedData) -> List[RequirementNode]:
        """
        解析document.js文件
        Parse document.js file
        
        document.js格式示例 document.js format example:
        var a="登录",b="id123",c="pageName";
        _(s,t,u,v,w,x,y,z,A,[children])
        """
        if not isinstance(data.body, str):
            return []
        
        nodes = []
        content = data.body
        
        # 提取变量定义
        variables = {}
        for match in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"', content):
            variables[match.group(1)] = match.group(2)
        
        # 解析页面名称
        # 通常格式: _(id_var, u, name_var, ...)
        # 其中name_var对应variables中的页面名称
        
        # 查找所有可能的页面名称
        for var_name, value in variables.items():
            # 过滤掉明显不是页面名称的变量
            if len(value) > 1 and len(value) < 50 and not value.startswith("http"):
                # 检查是否包含中文（墨刀页面名通常是中文）
                if re.search(r'[\u4e00-\u9fa5]', value):
                    node = RequirementNode(
                        id=f"modao_{var_name}",
                        name=value,
                        page_id=var_name,
                        url=data.url
                    )
                    nodes.append(node)
        
        return nodes
    
    async def _parse_api_data(self, data: SniffedData) -> List[RequirementNode]:
        """解析API返回的JSON数据"""
        if not isinstance(data.body, dict):
            return []
        
        nodes = []
        
        # 尝试从不同的API响应格式中提取页面
        pages = data.body.get("pages", []) or data.body.get("data", [])
        
        for page in pages:
            if isinstance(page, dict):
                page_id = page.get("id", "") or page.get("pageId", "")
                page_name = page.get("name", "") or page.get("pageName", "")
                
                if page_name:
                    # 提取元素
                    elements = []
                    components = page.get("components", []) or page.get("elements", [])
                    
                    for comp in components:
                        element = UIElement(
                            id=comp.get("id", ""),
                            type=self._map_element_type(comp.get("type", "")),
                            name=comp.get("name", ""),
                            text=comp.get("text", ""),
                            attributes=comp
                        )
                        elements.append(element)
                    
                    node = RequirementNode(
                        id=f"modao_{page_id}",
                        name=page_name,
                        page_id=page_id,
                        url=page.get("url", ""),
                        elements=elements,
                        raw_data=page
                    )
                    nodes.append(node)
        
        return nodes
    
    async def _parse_sitemap(self, data: SniffedData) -> List[RequirementNode]:
        """解析站点地图数据"""
        if isinstance(data.body, dict):
            items = data.body.get("items", []) or data.body.get("children", [])
        elif isinstance(data.body, list):
            items = data.body
        else:
            return []
        
        nodes = []
        
        def parse_items(items: List, parent: str = ""):
            for item in items:
                if isinstance(item, dict):
                    page_name = item.get("name", "") or item.get("text", "")
                    page_id = item.get("id", "") or item.get("pageId", "")
                    
                    if page_name:
                        node = RequirementNode(
                            id=f"modao_sitemap_{page_id}",
                            name=page_name,
                            page_id=page_id,
                            url=item.get("url", "")
                        )
                        nodes.append(node)
                    
                    # 递归处理子项
                    children = item.get("children", []) or item.get("items", [])
                    if children:
                        parse_items(children, page_name)
                
                elif isinstance(item, str) and item.strip():
                    # 纯文本项
                    node = RequirementNode(
                        id=f"modao_sitemap_{len(nodes)}",
                        name=item.strip(),
                        page_id=f"sitemap_{len(nodes)}"
                    )
                    nodes.append(node)
        
        parse_items(items)
        return nodes
    
    def _map_element_type(self, type_str: str) -> ElementType:
        """映射元素类型 Map element type"""
        type_map = {
            "button": ElementType.BUTTON,
            "input": ElementType.INPUT,
            "text": ElementType.TEXT,
            "image": ElementType.IMAGE,
            "link": ElementType.LINK,
            "container": ElementType.CONTAINER,
        }
        return type_map.get(type_str.lower(), ElementType.UNKNOWN)
