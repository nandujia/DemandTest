"""
调度中心
"""

from typing import Dict, Any, Optional, List
from ..llm import BaseLLM, Message, MessageRole, LLMFactory
from ..knowledge import KnowledgeBase
from ..models.llm_config import LLMProfile
from ..services.config_service import ConfigService
from .session import SessionManager, SessionState
from .intent_agent import IntentAgent, Intent, IntentResult
from ..skills.base import SkillResult
from ..skills.registry import SkillRegistry
from ..skills.analyze_skill import AnalyzeSkill
from ..skills.testcase_skill import TestCaseSkill
from ..skills.export_skill import ExportSkill
from ..skills.qa_skill import QASkill


class Orchestrator:
    """调度中心 - 核心"""
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        config_service: Optional[ConfigService] = None
    ):
        self.llm = llm
        self.knowledge_base = knowledge_base
        self.config_service = config_service or ConfigService()
        
        self.session_manager = SessionManager()
        self.intent_agent = IntentAgent(llm=llm)
        
        # 注册技能
        self._register_skills()
    
    def _register_skills(self):
        """注册技能"""
        SkillRegistry.register(AnalyzeSkill)
        SkillRegistry.register(TestCaseSkill)
        SkillRegistry.register(ExportSkill)
        SkillRegistry.register(QASkill)
    
    def process(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息
            session_id: 会话ID
            
        Returns:
            处理结果
        """
        # 1. 获取或创建会话
        session = self.session_manager.get_or_create(session_id)
        
        # 2. 记录用户消息
        self.session_manager.add_message(session.session_id, "user", user_message)
        
        # 3. 意图识别
        intent_result = self.intent_agent.analyze(user_message, session)
        
        # 4. 路由到对应技能
        result = self._route_to_skill(intent_result, session)
        
        # 5. 生成回复
        response = self._generate_response(result, session)
        
        # 6. 记录回复
        self.session_manager.add_message(session.session_id, "assistant", response["message"])
        
        return {
            "session_id": session.session_id,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "success": result.success,
            "message": response["message"],
            "data": result.data,
            "suggestion": result.suggestion
        }
    
    def _route_to_skill(
        self,
        intent_result: IntentResult,
        session: SessionState
    ) -> SkillResult:
        """路由到技能"""
        
        intent_map = {
            Intent.ANALYZE_URL: "analyze",
            Intent.GENERATE_TESTCASE: "gen_testcase",
            Intent.EXPORT: "export",
            Intent.QA: "qa",
            Intent.HELP: "qa",
        }
        
        skill_name = intent_map.get(intent_result.intent)
        
        if not skill_name:
            # 未知意图
            return SkillResult(
                success=False,
                error="抱歉，我没有理解你的意思",
                suggestion="你可以试试：「分析 https://xxx」或「生成测试用例」"
            )
        
        # 获取技能实例
        skill = SkillRegistry.get_or_create(
            skill_name,
            llm=self.llm,
            knowledge_base=self.knowledge_base
        )
        
        if not skill:
            return SkillResult(
                success=False,
                error=f"技能 {skill_name} 不可用"
            )
        
        # 合并参数
        params = intent_result.entities.copy()
        
        # 检查缺失参数
        missing = skill.validate_params(params)
        if missing:
            return SkillResult(
                success=False,
                error="缺少必要参数",
                suggestion=skill.ask_clarification(missing)
            )
        
        # 执行技能
        return skill.execute(params, session)
    
    def _generate_response(
        self,
        result: SkillResult,
        session: SessionState
    ) -> Dict[str, str]:
        """生成回复"""
        
        if result.success:
            # 成功时，如果有 LLM，生成更友好的回复
            if self.llm and result.data:
                return self._enhance_response(result, session)
            
            return {"message": result.message}
        else:
            # 失败时返回错误和建议
            message = result.error or "操作失败"
            if result.suggestion:
                message += f"\n\n{result.suggestion}"
            return {"message": message}
    
    def _enhance_response(
        self,
        result: SkillResult,
        session: SessionState
    ) -> Dict[str, str]:
        """增强回复"""
        
        # 简单场景直接返回
        if len(result.message) < 50:
            return {"message": result.message}
        
        # 复杂场景使用 LLM 优化
        prompt = f"""将以下信息转换为更友好、自然的回复：

原始信息：
{result.message}

要求：
1. 保持简洁
2. 语气友好
3. 如有后续建议，可以加上

只返回回复内容，不要其他内容。
"""
        
        try:
            enhanced = self.llm.chat([
                Message(role=MessageRole.USER, content=prompt)
            ])
            return {"message": enhanced}
        except:
            return {"message": result.message}
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """获取会话上下文"""
        return self.session_manager.get_context_summary(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """清除会话"""
        return self.session_manager.delete(session_id)
