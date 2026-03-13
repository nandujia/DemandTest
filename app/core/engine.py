"""
编排引擎 - Workflow Orchestration Engine

核心职责 Core Responsibilities:
1. 协调各技能执行 | Coordinate skill execution
2. 管理状态流转 | Manage state transitions
3. 集成自学习服务 | Integrate self-learning service
4. 提供进度回调 | Provide progress callbacks
"""

from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import inspect
import json
import re

from app.core.schema import (
    ExtractionResult,
    GenerationResult,
    RequirementNode,
    TestCase
)
from app.platforms.registry import PlatformRegistry
from app.adapters.sniffer import DataSniffer
from app.services.shadow_learning import get_shadow_learning
from app.services.async_tasks import get_task_manager
from app.model.base import BaseModelClient

# 获取日志器
logger = logging.getLogger(__name__)


class WorkflowState(str, Enum):
    """工作流状态 Workflow States"""
    IDLE = "idle"
    EXTRACTING = "extracting"       # 数据提取
    TRANSFORMING = "transforming"   # 数据转换
    GENERATING = "generating"       # 用例生成
    EXPORTING = "exporting"         # 导出文件
    COMPLETED = "completed"         # 完成
    FAILED = "failed"               # 失败


@dataclass
class WorkflowContext:
    """工作流上下文 Workflow Context"""
    url: str
    state: WorkflowState = WorkflowState.IDLE
    platform: str = ""
    
    # 各阶段结果
    extraction_result: Optional[ExtractionResult] = None
    test_cases: List[TestCase] = field(default_factory=list)
    export_path: Optional[str] = None
    
    # 元数据
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 进度回调
    progress_callback: Optional[Callable] = None


class Engine:
    """
    编排引擎
    Orchestration Engine
    
    协调数据提取、用例生成、文件导出的完整流程
    Coordinates the complete workflow of data extraction, test case generation, and export.
    
    使用示例 Usage Example:
        engine = Engine(llm=my_llm)
        result = await engine.run("https://modao.cc/xxx")
    """
    
    def __init__(
        self,
        llm: Optional[BaseModelClient] = None,
        use_shadow_learning: bool = True
    ):
        self.llm = llm
        self.use_shadow_learning = use_shadow_learning
        self.shadow_learning = get_shadow_learning() if use_shadow_learning else None
    
    async def run(
        self,
        url: str,
        pages: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        执行完整工作流
        Execute complete workflow
        
        Args:
            url: 原型链接 Prototyping link
            pages: 指定页面名称列表 Specific page names (optional)
            progress_callback: 进度回调函数 Progress callback
        
        Returns:
            工作流结果 Workflow result
        """
        ctx = WorkflowContext(
            url=url,
            started_at=datetime.now(),
            progress_callback=progress_callback
        )
        
        try:
            # Step 1: 数据提取 (30%)
            await self._update_progress(ctx, WorkflowState.EXTRACTING, 0, 3, "正在提取数据...")
            
            extraction_result = await self._extract(url)
            ctx.extraction_result = extraction_result
            ctx.platform = extraction_result.platform
            
            if not extraction_result.success:
                ctx.state = WorkflowState.FAILED
                ctx.error = extraction_result.error
                return self._build_response(ctx)
            
            await self._update_progress(ctx, WorkflowState.EXTRACTING, 1, 3, 
                f"已提取 {len(extraction_result.pages)} 个页面")
            
            # Step 2: 用例生成 (60%)
            if self.llm and extraction_result.pages:
                await self._update_progress(ctx, WorkflowState.GENERATING, 1, 3, "正在生成测试用例...")
                
                all_cases = []
                total_pages = len(extraction_result.pages)
                
                for i, page in enumerate(extraction_result.pages):
                    # 过滤指定页面
                    if pages and page.name not in pages:
                        continue
                    
                    # 更新进度
                    await self._update_progress(ctx, WorkflowState.GENERATING, 
                        1 + (i / total_pages), 3, f"生成中: {page.name}")
                    
                    # 生成测试用例
                    cases = await self._generate_test_cases(page)
                    all_cases.extend(cases)
                
                ctx.test_cases = all_cases
                
                await self._update_progress(ctx, WorkflowState.GENERATING, 2, 3,
                    f"已生成 {len(all_cases)} 条测试用例")
            
            # Step 3: 导出 (100%)
            if ctx.test_cases:
                await self._update_progress(ctx, WorkflowState.EXPORTING, 2, 3, "正在导出文件...")
                
                export_path = await self._export(ctx.test_cases)
                ctx.export_path = export_path
                
                await self._update_progress(ctx, WorkflowState.EXPORTING, 3, 3,
                    f"已导出到: {export_path}")
            
            ctx.state = WorkflowState.COMPLETED
            
        except Exception as e:
            ctx.state = WorkflowState.FAILED
            ctx.error = str(e)
            import traceback
            traceback.print_exc()
        
        ctx.completed_at = datetime.now()
        
        return self._build_response(ctx)
    
    async def generate(
        self,
        extraction_result: ExtractionResult,
        selected_pages: Optional[List[str]] = None
    ) -> List[TestCase]:
        """
        仅执行用例生成
        Execute test case generation only
        """
        all_cases = []
        
        for page in extraction_result.pages:
            # 过滤指定页面
            if selected_pages and (page.name not in selected_pages and page.id not in selected_pages):
                continue
            
            # 生成测试用例
            cases = await self._generate_test_cases(page)
            all_cases.extend(cases)
            
        return all_cases

    async def export_only(self, test_cases: List[TestCase]) -> str:
        """
        仅执行导出
        Execute export only
        """
        return await self._export(test_cases)

    async def _extract(self, url: str) -> ExtractionResult:
        """
        数据提取阶段
        Data extraction phase
        
        使用平台适配器进行协议级数据嗅探
        Uses platform adapter for protocol-level data sniffing.
        """
        # 获取平台适配器
        adapter = PlatformRegistry.get_adapter(url)
        
        if not adapter:
            return ExtractionResult(
                platform="unknown",
                url=url,
                success=False,
                error=f"不支持的平台 | Unsupported platform. Supported: {PlatformRegistry.list_platforms()}"
            )
        
        # 执行提取
        return await adapter.extract(url)
    
    async def _generate_test_cases(
        self,
        requirement: RequirementNode
    ) -> List[TestCase]:
        """
        测试用例生成阶段
        Test case generation phase
        
        使用LLM生成测试用例，集成Few-Shot学习
        Uses LLM to generate test cases with Few-Shot learning.
        """
        if not self.llm:
            return self._fallback_test_cases(requirement)
        
        prompt = f"""你是专业的测试工程师。请针对下面的页面需求生成测试用例，并严格按 JSON 输出。

{requirement.to_prompt_text()}

要求：
- 输出必须是 JSON 数组，每个元素为一个测试用例对象
- 不要输出除 JSON 之外的任何文字

每个测试用例对象字段：
- title: string
- priority: one of ["P0","P1","P2","P3"]
- type: one of ["positive","negative","boundary","exception","security"]
- preconditions: string[]
- steps: [{ "order": number, "action": string, "expected": string }]
- expected_result: string

请至少生成 4 条用例，覆盖：正向、逆向、边界、异常/安全。
"""
        
        # 使用影子学习增强Prompt
        if self.shadow_learning:
            prompt = self.shadow_learning.build_few_shot_prompt(
                prompt,
                requirement.to_prompt_text()
            )
        
        # 调用LLM生成
        try:
            from app.model import Message, MessageRole
            
            response = await self.llm.achat([
                Message(role=MessageRole.SYSTEM, content="You are a senior QA engineer."),
                Message(role=MessageRole.USER, content=prompt),
            ])
            
            cases = self._parse_test_cases(response, requirement)
            
            return cases
            
        except Exception as e:
            logger.info(f"[Engine] 生成失败: {e}")
            return self._fallback_test_cases(requirement)

    def _fallback_test_cases(self, requirement: RequirementNode) -> List[TestCase]:
        from app.core.schema import TestCaseStep
        return [
            TestCase(
                id=f"TC_{requirement.id}_F001",
                title=f"正向-{requirement.name}-基础流程",
                module=requirement.name,
                priority="P1",
                type="positive",
                preconditions=[],
                steps=[
                    TestCaseStep(order=1, action="进入页面", expected="页面正常打开"),
                    TestCaseStep(order=2, action="按页面提示完成操作", expected="操作成功并有正确反馈"),
                ],
                expected_result="页面核心功能可用"
            ),
            TestCase(
                id=f"TC_{requirement.id}_F002",
                title=f"逆向-{requirement.name}-必填/校验",
                module=requirement.name,
                priority="P1",
                type="negative",
                preconditions=[],
                steps=[
                    TestCaseStep(order=1, action="输入非法/缺失数据并提交", expected="出现明确校验提示"),
                ],
                expected_result="校验与提示符合预期"
            ),
            TestCase(
                id=f"TC_{requirement.id}_F003",
                title=f"边界-{requirement.name}-输入边界",
                module=requirement.name,
                priority="P2",
                type="boundary",
                preconditions=[],
                steps=[
                    TestCaseStep(order=1, action="使用最小/最大长度边界值输入并提交", expected="系统处理正确"),
                ],
                expected_result="边界输入处理正确"
            ),
            TestCase(
                id=f"TC_{requirement.id}_F004",
                title=f"异常-{requirement.name}-网络/接口异常",
                module=requirement.name,
                priority="P2",
                type="exception",
                preconditions=[],
                steps=[
                    TestCaseStep(order=1, action="模拟接口失败或超时", expected="页面给出可理解的错误与重试入口"),
                ],
                expected_result="异常场景可感知且可恢复"
            ),
        ]
    
    def _parse_test_cases(
        self,
        response: str,
        requirement: RequirementNode
    ) -> List[TestCase]:
        """
        解析LLM响应为测试用例
        Parse LLM response to test cases
        
        TODO: 使用Pydantic结构化输出确保100%可解析
        """
        from app.core.schema import TestCaseStep

        from app.core.schema import TestCaseStep

        if not response:
            response = ""

        raw = response.strip()
        m = re.search(r"```json\s*([\s\S]*?)```", raw, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()

        data = None
        list_start = raw.find("[")
        list_end = raw.rfind("]")
        if list_start != -1 and list_end != -1 and list_end > list_start:
            try:
                data = json.loads(raw[list_start:list_end + 1])
            except Exception:
                data = None
        if data is None:
            obj_start = raw.find("{")
            obj_end = raw.rfind("}")
            if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
                try:
                    data = json.loads(raw[obj_start:obj_end + 1])
                except Exception:
                    data = None

        if isinstance(data, dict) and isinstance(data.get("test_cases"), list):
            data = data["test_cases"]

        if not isinstance(data, list):
            data = []

        cases: List[TestCase] = []
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                continue

            steps: List[TestCaseStep] = []
            raw_steps = item.get("steps") or []
            if isinstance(raw_steps, list):
                for s in raw_steps:
                    if isinstance(s, dict):
                        try:
                            steps.append(TestCaseStep(
                                order=int(s.get("order", len(steps) + 1)),
                                action=str(s.get("action", "")).strip(),
                                expected=str(s.get("expected", "")).strip() if s.get("expected") is not None else None
                            ))
                        except Exception:
                            continue

            title = str(item.get("title") or "").strip()
            expected_result = str(item.get("expected_result") or "").strip()
            if not title or not expected_result:
                continue

            cases.append(TestCase(
                id=f"TC_{requirement.id}_{idx:03d}",
                title=title,
                module=requirement.name,
                priority=item.get("priority") or "P2",
                type=item.get("type") or "positive",
                preconditions=item.get("preconditions") if isinstance(item.get("preconditions"), list) else [],
                steps=steps,
                expected_result=expected_result
            ))

        if cases:
            return cases

        return [
            TestCase(
                id=f"TC_{requirement.id}_001",
                title=f"正向-{requirement.name}功能验证",
                module=requirement.name,
                expected_result="功能正常工作",
                steps=[
                    TestCaseStep(order=1, action=f"进入{requirement.name}页面", expected="页面加载成功"),
                    TestCaseStep(order=2, action="执行核心操作", expected="操作成功完成")
                ]
            ),
            TestCase(
                id=f"TC_{requirement.id}_002",
                title=f"逆向-{requirement.name}异常输入",
                module=requirement.name,
                type="negative",
                expected_result="正确处理异常",
                steps=[
                    TestCaseStep(order=1, action=f"进入{requirement.name}页面", expected="页面加载成功"),
                    TestCaseStep(order=2, action="输入非法数据并提交", expected="提示错误且提交失败")
                ]
            )
        ]
    
    async def _export(self, test_cases: List[TestCase]) -> str:
        """
        导出测试用例
        Export test cases
        
        导出为Excel格式
        Exports to Excel format.
        """
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from datetime import datetime
        from pathlib import Path
        
        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "测试用例"
        
        # 表头
        headers = ["ID", "标题", "模块", "优先级", "类型", "前置条件", "操作步骤", "预期结果"]
        ws.append(headers)
        
        # 数据
        for case in test_cases:
            ws.append([
                case.id,
                case.title,
                case.module or "",
                case.priority,
                case.type,
                "\n".join(case.preconditions),
                "\n".join([f"{s.order}. {s.action}" for s in case.steps]),
                case.expected_result
            ])
        
        # 保存
        export_dir = Path("./exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = export_dir / f"test_cases_{timestamp}.xlsx"
        
        wb.save(filepath)
        
        return str(filepath)
    
    async def _update_progress(
        self,
        ctx: WorkflowContext,
        state: WorkflowState,
        current: float,
        total: float,
        message: str
    ):
        """更新进度 Update progress"""
        ctx.state = state
        
        if ctx.progress_callback:
            try:
                result = ctx.progress_callback({
                    "state": state.value,
                    "current": current,
                    "total": total,
                    "percentage": round(current / total * 100, 1) if total > 0 else 0,
                    "message": message
                })
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
        
        logger.info(f"[Engine] {state.value}: {message} ({current}/{total})")
    
    def _build_response(self, ctx: WorkflowContext) -> Dict[str, Any]:
        """构建响应 Build response"""
        elapsed = (ctx.completed_at - ctx.started_at).total_seconds() if ctx.completed_at else 0
        
        return {
            "state": ctx.state.value,
            "url": ctx.url,
            "platform": ctx.platform,
            "extraction": {
                "success": ctx.extraction_result.success if ctx.extraction_result else False,
                "pages_count": len(ctx.extraction_result.pages) if ctx.extraction_result else 0,
                "elements_count": ctx.extraction_result.total_elements if ctx.extraction_result else 0
            },
            "test_cases": {
                "count": len(ctx.test_cases),
                "items": [case.model_dump() for case in ctx.test_cases]
            },
            "export_path": ctx.export_path,
            "error": ctx.error,
            "elapsed_seconds": round(elapsed, 2)
        }
    
    async def extract_only(self, url: str, storage_state: Optional[str] = None) -> ExtractionResult:
        """
        仅执行数据提取
        Execute data extraction only
        
        用于测试和调试
        For testing and debugging.
        """
        adapter = PlatformRegistry.get_adapter(url)
        if not adapter:
            return ExtractionResult(
                platform="unknown",
                url=url,
                success=False,
                error=f"不支持的平台 | Unsupported platform. Supported: {PlatformRegistry.list_platforms()}"
            )
        return await adapter.extract(url, storage_state=storage_state)
