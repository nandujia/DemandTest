"""
测试用例生成技能
"""

from typing import Dict, Any, List, Optional
from .base import BaseSkill, SkillResult
from ..core.session import SessionState


class TestCaseSkill(BaseSkill):
    """生成测试用例"""
    
    name = "gen_testcase"
    description = "根据需求生成测试用例"
    triggers = ["生成测试用例", "写测试用例", "生成用例"]
    
    parameters = {
        "pages": {"required": False, "description": "页面列表（可选，默认使用当前分析的所有页面）"},
        "types": {"required": False, "description": "测试类型"},
        "priority": {"required": False, "description": "优先级"}
    }
    
    def execute(
        self,
        params: Dict[str, Any],
        session: SessionState
    ) -> SkillResult:
        """执行用例生成"""
        
        # 获取页面列表
        pages = params.get("pages")
        filter_keyword = params.get("filter")
        
        if not pages:
            pages = session.analyzed_pages
            if not pages:
                return SkillResult(
                    success=False,
                    error="没有可用的页面数据",
                    suggestion="请先分析一个原型链接，发送「分析 https://xxx」"
                )
        
        # 筛选
        if filter_keyword:
            pages = [p for p in pages if filter_keyword in p.get("name", "")]
            if not pages:
                return SkillResult(
                    success=False,
                    error=f"没有找到包含「{filter_keyword}」的页面",
                    suggestion="请检查筛选关键词，或使用其他关键词"
                )
        
        # 测试类型
        test_types = params.get("types", ["positive", "negative"])
        priority = params.get("priority", "P1")
        
        # 生成测试用例
        test_cases = self._generate(pages, test_types, priority, session)
        
        # 更新会话
        session.test_cases = test_cases
        
        # 统计
        type_counts = {}
        for tc in test_cases:
            t = tc.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        type_summary = ", ".join([f"{k}: {v}" for k, v in type_counts.items()])
        
        return SkillResult(
            success=True,
            data={
                "test_cases": test_cases,
                "total": len(test_cases),
                "pages_count": len(pages),
                "type_summary": type_summary
            },
            message=f"已生成 {len(test_cases)} 条测试用例（{type_summary}）"
        )
    
    def _generate(
        self,
        pages: List[Dict],
        test_types: List[str],
        priority: str,
        session: SessionState
    ) -> List[Dict]:
        """生成测试用例"""
        
        # 使用 LLM 增强
        if self.llm:
            return self._llm_generate(pages, test_types, priority, session)
        
        # 使用模板生成
        return self._template_generate(pages, test_types, priority)
    
    def _template_generate(
        self,
        pages: List[Dict],
        test_types: List[str],
        priority: str
    ) -> List[Dict]:
        """模板生成"""
        from ..services.generator.test_case_generator import TestCaseGenerator
        
        generator = TestCaseGenerator()
        page_names = [p.get("name", "") for p in pages]
        
        return generator.generate(page_names, test_types, priority)
    
    def _llm_generate(
        self,
        pages: List[Dict],
        test_types: List[str],
        priority: str,
        session: SessionState
    ) -> List[Dict]:
        """使用 LLM 生成"""
        import json
        import re
        
        page_names = [p.get("name", "") for p in pages]
        
        # 获取知识库上下文
        context = ""
        if self.knowledge_base and session:
            query = " ".join(page_names[:5])
            try:
                context = self.knowledge_base.get_context(query, top_k=3)
            except:
                pass
        
        prompt = f"""根据以下页面生成测试用例：

页面列表：{json.dumps(page_names, ensure_ascii=False, indent=2)}

测试类型：{', '.join(test_types)}
优先级：{priority}

{f'参考知识库内容：{context}' if context else ''}

请生成测试用例，以 JSON 数组格式输出：
[
  {{
    "id": "TC_模块_001",
    "title": "测试用例标题",
    "preconditions": "前置条件",
    "steps": "操作步骤",
    "expected_results": "预期结果",
    "priority": "{priority}",
    "type": "positive/negative/boundary"
  }}
]

只返回 JSON 数组，不要其他内容。
"""
        
        try:
            from ..llm import Message, MessageRole
            response = self.llm.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # 解析 JSON
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 失败时使用模板
        return self._template_generate(pages, test_types, priority)
