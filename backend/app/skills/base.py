"""
技能基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from ..llm import BaseLLM
from ..knowledge import KnowledgeBase
from .session import SessionState


class SkillResult(BaseModel):
    """技能执行结果"""
    success: bool
    data: Dict[str, Any] = {}
    message: str = ""
    error: Optional[str] = None
    suggestion: Optional[str] = None
    requires_action: bool = False  # 是否需要用户进一步操作


class BaseSkill(ABC):
    """技能基类"""
    
    name: str = ""
    description: str = ""
    triggers: List[str] = []
    parameters: Dict[str, Any] = {}
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        self.llm = llm
        self.knowledge_base = knowledge_base
    
    @abstractmethod
    def execute(
        self,
        params: Dict[str, Any],
        session: SessionState
    ) -> SkillResult:
        """
        执行技能
        
        Args:
            params: 参数
            session: 会话状态
            
        Returns:
            执行结果
        """
        pass
    
    def can_handle(self, intent: str, params: Dict[str, Any]) -> bool:
        """判断是否能处理"""
        return intent == self.name
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """验证参数，返回缺失参数列表"""
        missing = []
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False) and param_name not in params:
                missing.append(param_name)
        return missing
    
    def ask_clarification(self, missing_params: List[str]) -> str:
        """请求用户澄清"""
        param_names = {
            "url": "原型链接",
            "pages": "页面名称",
            "format": "导出格式",
            "content": "文档内容"
        }
        
        names = [param_names.get(p, p) for p in missing_params]
        return f"请提供以下信息：{', '.join(names)}"
