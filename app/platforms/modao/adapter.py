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
from typing import Dict, List, Any, Optional, Tuple

import httpx

from app.platforms.base import BasePlatformAdapter, PlatformInfo
from app.core.schema import RequirementNode, UIElement, ElementType, ExtractionResult
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

    async def extract(self, url: str, storage_state: Optional[str] = None):
        preflight_error = await self._preflight_error(url)
        if preflight_error:
            return ExtractionResult(
                platform=self.info.name,
                url=url,
                pages=[],
                total_elements=0,
                success=False,
                error=preflight_error
            )

        result = await super().extract(url, storage_state=storage_state)
        if result.success:
            return result

        cached = self.get_cached_data()
        if self._looks_like_deleted_or_missing(cached):
            result.error = "墨刀链接无效：找不到文件或已被删除，请联系分享者重新生成分享链接。"
        return result
    
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
                "/api/",
                "/api/upper/",
                "/api/upper/web_v1/design/init",
                "design/init",
                "init2403",
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
                "/go/v1/axfile/axdata",
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
        meta, fallback_doc = self._collect_axdata_meta(sniffed_data)
        
        for data in sniffed_data:
            if data.source == "document_js":
                # 解析document.js
                parsed_nodes = await self._parse_document_js(data, meta=meta)
                for node in parsed_nodes:
                    if node.page_id not in seen_page_ids:
                        nodes.append(node)
                        seen_page_ids.add(node.page_id)
            
            elif data.source in ("api", "workspace", "json_api", "data_endpoint"):
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
            elif data.source == "axdata":
                if isinstance(data.body, str) and "document.js" in (data.url or ""):
                    parsed_nodes = await self._parse_document_js(data, meta=meta)
                    for node in parsed_nodes:
                        if node.page_id not in seen_page_ids:
                            nodes.append(node)
                            seen_page_ids.add(node.page_id)
        
        if not nodes and fallback_doc:
            parsed_nodes = self._parse_document_js_content(fallback_doc, url=meta.get("document_url") or "")
            for node in parsed_nodes:
                if node.page_id not in seen_page_ids:
                    nodes.append(node)
                    seen_page_ids.add(node.page_id)

        if not nodes and meta.get("document_url"):
            fetched = await self._fetch_document_js(str(meta["document_url"]))
            if fetched:
                parsed_nodes = self._parse_document_js_content(fetched, url=str(meta["document_url"]))
                for node in parsed_nodes:
                    if node.page_id not in seen_page_ids:
                        nodes.append(node)
                        seen_page_ids.add(node.page_id)

        return nodes

    def _looks_like_deleted_or_missing(self, cached: List[SniffedData]) -> bool:
        for pkt in cached:
            if pkt.status == 404:
                return True
            if isinstance(pkt.body, str):
                if "找不到文件" in pkt.body:
                    return True
                if "文件可能已被删除" in pkt.body:
                    return True
                if "page not found" in pkt.body.lower():
                    return True
            if isinstance(pkt.body, dict):
                msg = pkt.body.get("message") or pkt.body.get("msg") or ""
                if isinstance(msg, str) and ("找不到文件" in msg or "删除" in msg):
                    return True
        return False

    async def _preflight_error(self, url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception:
            return None

        if r.status_code == 404:
            return "墨刀链接无效：找不到文件或已被删除，请联系分享者重新生成分享链接。"

        ct = (r.headers.get("content-type") or "").lower()
        if "text/html" not in ct:
            return None

        text = r.text or ""
        if "找不到文件" in text or "文件可能已被删除" in text:
            return "墨刀链接无效：找不到文件或已被删除，请联系分享者重新生成分享链接。"
        return None
    
    async def _parse_document_js(self, data: SniffedData, meta: Optional[Dict[str, Any]] = None) -> List[RequirementNode]:
        """
        解析document.js文件
        Parse document.js file
        
        document.js格式示例 document.js format example:
        var a="登录",b="id123",c="pageName";
        _(s,t,u,v,w,x,y,z,A,[children])
        """
        if not isinstance(data.body, str):
            return []
        
        nodes = self._parse_document_js_content(data.body, url=data.url or "")
        if meta:
            for n in nodes:
                n.raw_data = {**(n.raw_data or {}), "modao_meta": meta}
        return nodes

    def _collect_axdata_meta(self, sniffed_data: List[SniffedData]) -> Tuple[Dict[str, Any], Optional[str]]:
        meta: Dict[str, Any] = {}
        doc_candidates: List[SniffedData] = []

        for d in sniffed_data:
            if d.source != "axdata":
                continue

            if isinstance(d.body, dict) and ("page_count" in d.body or "project_cid" in d.body):
                meta["axdata"] = d.body
                meta["axdata_url"] = d.url

            if isinstance(d.body, dict) and isinstance(d.body.get("token"), str) and d.body.get("token"):
                meta["file_id"] = d.body["token"]
                meta["token_url"] = d.url

            if isinstance(d.url, str):
                m = re.search(r"/go/v1/axfile/files/([^/]+)/start\.html", d.url)
                if m:
                    meta["file_id"] = m.group(1)
                    meta["start_url"] = d.url

            if isinstance(d.body, str) and "document.js" in (d.url or ""):
                doc_candidates.append(d)

        if "file_id" in meta and "document_url" not in meta:
            meta["document_url"] = f"https://axdata.modao.ink/go/v1/axfile/files/{meta['file_id']}/data/document.js"

        if doc_candidates:
            doc_candidates.sort(key=lambda x: len(x.body) if isinstance(x.body, str) else 0, reverse=True)
            return meta, doc_candidates[0].body if isinstance(doc_candidates[0].body, str) else None

        return meta, None

    async def _fetch_document_js(self, url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception:
            return None

        if r.status_code != 200:
            return None
        return r.text or None

    def _parse_document_js_content(self, content: str, url: str = "") -> List[RequirementNode]:
        variables: Dict[str, str] = {}
        for match in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"', content):
            variables[match.group(1)] = match.group(2)

        sitemap = self._extract_sitemap_array(content)
        if not sitemap:
            return []

        items = self._parse_node_array(sitemap, variables)
        pages: List[RequirementNode] = []

        def walk(node: Dict[str, Any]):
            if not isinstance(node, dict):
                return
            if not node.get("is_folder"):
                page_id = (node.get("page_id") or "").strip()
                page_name = (node.get("name") or "").strip()
                if page_id and page_name:
                    pages.append(
                        RequirementNode(
                            id=f"modao_{page_id}",
                            name=page_name,
                            page_id=page_id,
                            url=url,
                            raw_data=node
                        )
                    )
            children = node.get("children") or []
            if isinstance(children, list):
                for c in children:
                    walk(c)

        for item in items:
            walk(item)

        return pages

    def _extract_sitemap_array(self, content: str) -> Optional[str]:
        idx = content.find("r,[")
        if idx == -1:
            return None

        j = idx + 2
        bracket_count = 0
        start = j
        while j < len(content):
            c = content[j]
            if c == "[":
                bracket_count += 1
            elif c == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    return content[start : j + 1]
            j += 1
        return None

    def _parse_node_array(self, s: str, variables: Dict[str, str]) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        i = 0
        while i < len(s):
            if s[i : i + 4] != "_(s,":
                i += 1
                continue

            bracket_count = 0
            j = i
            while j < len(s):
                c = s[j]
                if c == "(":
                    bracket_count += 1
                elif c == ")":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
                j += 1

            node_str = s[i + 2 : j]
            node = self._parse_node(node_str, variables)
            if node:
                nodes.append(node)
            i = j + 1
        return nodes

    def _parse_node(self, node_str: str, variables: Dict[str, str]) -> Optional[Dict[str, Any]]:
        match = re.match(r"s,([^,]+),u,([^,]+)", node_str)
        if not match:
            return None

        id_var = match.group(1)
        name_var = match.group(2)

        page_id = variables.get(id_var, id_var)
        page_name = variables.get(name_var, "")
        if not page_name:
            return None

        children: List[Dict[str, Any]] = []
        children_match = re.search(r"A,\[(.+)\]$", node_str)
        if children_match:
            children = self._parse_node_array(children_match.group(1), variables)

        is_folder = ",cW," in node_str
        return {
            "page_id": page_id,
            "name": page_name,
            "is_folder": is_folder,
            "children": children
        }
    
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
