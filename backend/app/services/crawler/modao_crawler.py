"""
墨刀爬虫服务 - API 监听方案

核心技术：
1. 使用 Playwright 访问墨刀分享链接
2. 监听 axdata.modao.ink 域名的网络请求
3. 捕获 data/document.js 文件（包含页面元数据）
4. 解析 Axure 格式，提取页面名称
"""

import re
import time
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright


class ModaoCrawler:
    """墨刀 API 爬取器"""
    
    def __init__(self, timeout: int = 60, headless: bool = True):
        self.timeout = timeout
        self.headless = headless
        self.document_content = None
        self.document_url = None
    
    def crawl(self, url: str) -> Dict:
        """
        爬取墨刀原型
        
        Args:
            url: 墨刀分享链接
            
        Returns:
            包含页面列表的字典
        """
        expected_count = 0
        pages = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # 监听网络请求
            def handle_response(response):
                resp_url = response.url
                # 捕获 document.js
                if 'axdata.modao' in resp_url and 'data/document' in resp_url:
                    try:
                        self.document_url = resp_url
                        self.document_content = response.text()
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # 访问页面
            page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 获取期望的页面数量
            page_text = page.evaluate("() => document.body.innerText")
            page_count_match = re.search(r'页面[（(](\d+)[）)]', page_text)
            if page_count_match:
                expected_count = int(page_count_match.group(1))
            
            browser.close()
        
        if not self.document_content:
            return {
                "success": False,
                "error": "未能获取 document.js",
                "expected": 0,
                "extracted": 0,
                "match_rate": "0%",
                "pages": []
            }
        
        # 解析页面列表
        pages = self._parse_document()
        
        # 计算匹配率
        match_rate = len(pages) / expected_count * 100 if expected_count > 0 else 0
        
        return {
            "success": True,
            "expected": expected_count,
            "extracted": len(pages),
            "match_rate": f"{match_rate:.1f}%",
            "pages": [{"id": str(i), "name": p, "status": self._get_status(p)} for i, p in enumerate(pages, 1)]
        }
    
    def _parse_document(self) -> List[str]:
        """
        解析 document.js 提取页面名称
        
        核心方法：从 .html 文件名提取页面名称（最准确）
        """
        pages = []
        
        # 提取 .html 文件名（最准确）
        html_files = re.findall(r'"([^"]+\.html)"', self.document_content)
        
        for f in html_files:
            name = f.replace('.html', '')
            
            # 过滤有效的页面名称
            if 2 < len(name) < 50:
                # 排除样式名称
                if not name.startswith('_'):
                    if '号字' not in name:
                        pages.append(name)
        
        return sorted(set(pages))
    
    def _get_status(self, page_name: str) -> Optional[str]:
        """获取页面状态"""
        if '（新增）' in page_name or '(新增)' in page_name:
            return "新增"
        elif '（修改）' in page_name or '(修改)' in page_name:
            return "修改"
        return None


# ==================== 平台识别 ====================

PLATFORM_PATTERNS = {
    "modao": [r"modao\.cc"],
    "lanhu": [r"lanhuapp\.com"],
    "axure": [r"share\.axure\.com", r"axshare\.com"],
    "mokc": [r"mokc\.cn"],
    "figma": [r"figma\.com"],
    "jsdesign": [r"js\.design"],
}


def identify_platform(url: str) -> Optional[str]:
    """识别 URL 对应的平台"""
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return None


# ==================== 统一入口 ====================

def crawl_url(url: str) -> Dict:
    """
    爬取 URL（统一入口）
    
    自动识别平台并调用对应的爬虫
    """
    platform = identify_platform(url)
    
    if platform == "modao":
        crawler = ModaoCrawler()
        return crawler.crawl(url)
    else:
        # 其他平台待实现
        return {
            "success": False,
            "error": f"平台 {platform} 暂不支持",
            "expected": 0,
            "extracted": 0,
            "match_rate": "0%",
            "pages": []
        }
