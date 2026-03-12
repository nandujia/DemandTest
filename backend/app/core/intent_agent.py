"""
意图识别 Agent
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from ..llm import BaseLLM, Message, MessageRole
from .session import SessionState


class Intent(str, Enum):
    """意图类型"""
    ANALYZE_URL = "analyze_url"              # 分析原型链接
    GENERATE_TESTCASE = "gen_testcase"       # 生成测试用例
    EXPORT = "export"                         # 导出
    UPLOAD_DOC = "upload_doc"                # 上传文档
    SEARCH_KB = "search_kb"                  # 检索知识库
    QA = "qa"                                # 问答
    REPORT = "report"                        # 生成报告
    CONFIG = "config"                        # 配置
    HELP = "help"                            # 帮助
    UNKNOWN = "unknown"                      # 未知


class IntentResult(BaseModel):
    """意图识别结果"""
    intent: Intent
    entities: Dict[str, Any] = {}
    confidence: float = 0.0
    missing_params: List[str] = []
    sub_intents: List[Intent] = []
    raw_response: Optional[str] = None


INTENT_ANALYSIS_PROMPT = """你是一个意图识别助手。分析用户消息，返回结构化意图。

## 支持的意图

| 意图 | 说明 | 触发词示例 |
|------|------|-----------|
| analyze_url | 分析原型链接 | 分析、看看、提取需求、解析原型 |
| gen_testcase | 生成测试用例 | 生成测试用例、写用例 |
| export | 导出文件 | 导出、下载、保存Excel |
| upload_doc | 上传文档 | 上传文档、添加文档 |
| search_kb | 检索知识库 | 查询、搜索知识库 |
| qa | 问答咨询 | 有什么功能、怎么用、是什么 |
| report | 生成报告 | 生成报告、分析报告 |
| config | 配置设置 | 设置、配置模型、修改配置 |
| help | 帮助 | 帮助、怎么用、使用说明 |

## 会话上下文

当前状态：
- 已分析的原型：{context_summary}
- 已生成的用例数：{test_cases_count}

## 用户消息

{user_message}

## 返回格式（JSON）

```json
{{
  "intent": "意图名称",
  "entities": {{
    "url": "提取的URL（如有）",
    "filter": "筛选条件（如有）",
    "format": "导出格式（如有）",
    "platform": "平台名称（如有）"
  }},
  "confidence": 0.95,
  "missing_params": ["缺少的参数（如有）"],
  "sub_intents": ["子意图（如有）"]
}}
```

只返回 JSON，不要其他内容。
"""


class IntentAgent:
    """意图识别 Agent"""
    
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm
    
    def analyze(
        self,
        user_message: str,
        session: Optional[SessionState] = None
    ) -> IntentResult:
        """
        分析用户意图
        
        Args:
            user_message: 用户消息
            session: 会话状态
            
        Returns:
            意图识别结果
        """
        # 1. 规则匹配（快速路径）
        rule_result = self._rule_based_match(user_message, session)
        if rule_result and rule_result.confidence > 0.9:
            return rule_result
        
        # 2. LLM 分析
        if self.llm:
            return self._llm_analyze(user_message, session)
        
        # 3. 返回规则结果或默认
        return rule_result or IntentResult(
            intent=Intent.UNKNOWN,
            confidence=0.0
        )
    
    def _rule_based_match(
        self,
        message: str,
        session: Optional[SessionState]
    ) -> Optional[IntentResult]:
        """基于规则的意图匹配"""
        message_lower = message.lower()
        
        # URL 分析
        if self._contains_url(message):
            url = self._extract_url(message)
            return IntentResult(
                intent=Intent.ANALYZE_URL,
                entities={"url": url},
                confidence=0.95
            )
        
        # 关键词匹配
        patterns = [
            (["分析", "看看", "提取需求", "解析原型"], Intent.ANALYZE_URL),
            (["生成测试用例", "写测试用例", "生成用例"], Intent.GENERATE_TESTCASE),
            (["导出", "下载", "保存excel", "导出excel"], Intent.EXPORT),
            (["上传", "添加文档"], Intent.UPLOAD_DOC),
            (["查询", "搜索知识"], Intent.SEARCH_KB),
            (["生成报告", "分析报告"], Intent.REPORT),
            (["设置", "配置"], Intent.CONFIG),
            (["帮助", "怎么用", "使用说明"], Intent.HELP),
        ]
        
        for keywords, intent in patterns:
            for keyword in keywords:
                if keyword in message_lower:
                    entities = {}
                    
                    # 从上下文推断参数
                    if intent == Intent.GENERATE_TESTCASE and session:
                        if session.analyzed_pages:
                            entities["pages"] = [p["name"] for p in session.analyzed_pages]
                    elif intent == Intent.EXPORT and session:
                        if session.test_cases:
                            entities["has_testcases"] = True
                    
                    return IntentResult(
                        intent=intent,
                        entities=entities,
                        confidence=0.85
                    )
        
        # 默认：QA 或未知
        return None
    
    def _llm_analyze(
        self,
        message: str,
        session: Optional[SessionState]
    ) -> IntentResult:
        """使用 LLM 分析意图"""
        context_summary = ""
        test_cases_count = 0
        
        if session:
            if session.current_url:
                context_summary = f"{session.current_platform}: {session.current_url}"
            test_cases_count = len(session.test_cases)
        
        prompt = INTENT_ANALYSIS_PROMPT.format(
            context_summary=context_summary,
            test_cases_count=test_cases_count,
            user_message=message
        )
        
        try:
            response = self.llm.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            
            # 解析 JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return IntentResult(
                    intent=Intent(data.get("intent", "unknown")),
                    entities=data.get("entities", {}),
                    confidence=data.get("confidence", 0.8),
                    missing_params=data.get("missing_params", []),
                    sub_intents=[Intent(i) for i in data.get("sub_intents", [])],
                    raw_response=response
                )
        except Exception as e:
            pass
        
        return IntentResult(intent=Intent.UNKNOWN, confidence=0.0)
    
    def _contains_url(self, message: str) -> bool:
        """检查是否包含 URL"""
        import re
        url_pattern = r'https?://[^\s]+'
        return bool(re.search(url_pattern, message))
    
    def _extract_url(self, message: str) -> Optional[str]:
        """提取 URL"""
        import re
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, message)
        return match.group(0) if match else None
