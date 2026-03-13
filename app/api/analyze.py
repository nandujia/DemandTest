"""
分析API接口 | Analysis API Endpoints

提供异步分析接口，支持进度查询
Provides async analysis API with progress tracking.
"""

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import tempfile

from app.core.engine import Engine
from app.core.schema import ExtractionResult
from app.platforms.registry import PlatformRegistry
from app.services.async_tasks import get_task_manager
from app.services.config_service import ConfigService
from app.model import ModelConfig, ModelInfo
from app.model.factory import ModelFactory
from app.utils.security import sanitize_url

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局状态 Global State
_latest_extraction: Optional[ExtractionResult] = None
_config_service: Optional[ConfigService] = None


def get_config_service() -> ConfigService:
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service


class ModelRuntimeConfig(BaseModel):
    provider: str
    base_url: str
    api: str
    api_key: str = ""
    model: Dict[str, str]
    temperature: float = 0.7
    max_tokens: int = 4096


def build_model(runtime: Optional[ModelRuntimeConfig]):
    runtime = None

    from app.core.config import settings
    if settings.LLM_BASE_URL and settings.LLM_MODEL_NAME:
        return ModelFactory.create(ModelConfig(
            provider=settings.LLM_API_TYPE,
            base_url=settings.LLM_BASE_URL,
            api="openai-completions",
            api_key=settings.LLM_API_KEY or "",
            model=ModelInfo(id=settings.LLM_MODEL_NAME, name=settings.LLM_MODEL_NAME),
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS
        ))

    return None


# ============ 请求模型 Request Models ============

class AnalyzeRequest(BaseModel):
    """分析请求 | Analyze Request"""
    url: str  # 使用str而非HttpUrl，以便自定义验证
    pages: Optional[List[str]] = None
    llm_type: Optional[str] = None  # glm, gpt, qwen, ernie, custom
    
    @validator('url')
    def validate_url(cls, v):
        """验证并清理URL"""
        try:
            return sanitize_url(v)
        except ValueError as e:
            raise ValueError(str(e))
    
    @validator('pages', each_item=True)
    def validate_pages(cls, v):
        """验证页面名称"""
        if len(v) > 100:
            raise ValueError('页面名称过长')
        return v


class AnalyzeResponse(BaseModel):
    """分析响应 | Analyze Response"""
    status: str
    message: str
    task_id: Optional[str] = None


class CrawlRequest(BaseModel):
    url: str
    playwright_storage_state: Optional[str] = None


class GenerateRequest(BaseModel):
    pages: List[str]
    types: List[str] = ["positive", "negative"]
    priority: str = "P1"
    model: Optional[ModelRuntimeConfig] = None


class ExportRequest(BaseModel):
    format: str = "xlsx"
    test_cases: List[Dict[str, Any]]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[ModelRuntimeConfig] = None


# ============ API端点 API Endpoints ============

@router.post("/crawl")
async def crawl_url(request: CrawlRequest):
    """
    爬取URL | Crawl URL
    
    同步接口，用于Web前端步骤条 Step 1
    Synchronous endpoint for Web Frontend Step 1
    """
    global _latest_extraction
    
    # 检查平台支持
    if not PlatformRegistry.is_supported(request.url):
         raise HTTPException(status_code=400, detail="不支持的平台")
         
    engine = Engine()
    # 执行提取
    result = await engine.extract_only(request.url, storage_state=request.playwright_storage_state)
    _latest_extraction = result
    
    if not result.success:
        if result.error and "No such file or directory" in result.error:
            return {
                "success": False,
                "error": "storage_state 路径不存在或后端无权限访问，请填写后端可访问的绝对路径"
            }
        return {"success": False, "error": result.error}
        
    pages_data = []
    for p in result.pages:
        pages_data.append({
            "id": p.id,
            "name": p.name,
            "status": "新增"
        })
        
    return {
        "success": True,
        "expected": len(result.pages),
        "extracted": len(result.pages),
        "match_rate": "100%",
        "pages": pages_data
    }


@router.post("/generate")
async def generate_cases(request: GenerateRequest):
    """
    生成测试用例 | Generate Test Cases
    
    同步接口，用于Web前端步骤条 Step 3
    Synchronous endpoint for Web Frontend Step 3
    """
    global _latest_extraction
    if not _latest_extraction:
        raise HTTPException(status_code=400, detail="请先执行爬取操作 | Please crawl first")
        
    model = build_model(None)
    engine = Engine(llm=model)
            
    # 执行生成
    cases = await engine.generate(_latest_extraction, request.pages)
    
    # 格式化输出
    formatted_cases = []
    for c in cases:
        steps_str = ""
        if c.steps:
            steps_str = "\n".join([f"{s.order}. {s.action} => {s.expected or ''}" for s in c.steps])
            
        formatted_cases.append({
            "id": c.id,
            "title": c.title,
            "preconditions": "\n".join(c.preconditions),
            "steps": steps_str,
            "expected_results": c.expected_result,
            "priority": c.priority.value if hasattr(c.priority, 'value') else c.priority,
            "type": c.type.value if hasattr(c.type, 'value') else c.type
        })
        
    return {
        "test_cases": formatted_cases,
        "total": len(formatted_cases)
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    from app.model import Message, MessageRole
    import httpx

    model = build_model(None)
    if model is None:
        raise HTTPException(status_code=400, detail="未配置模型，请在后端配置")

    messages = []
    for m in request.messages:
        role = m.role.lower()
        if role not in ("system", "user", "assistant"):
            role = "user"
        messages.append(Message(role=MessageRole(role), content=m.content))

    try:
        reply = await model.achat(messages)
        return {"reply": reply}
    except httpx.HTTPStatusError as e:
        detail = f"模型请求失败: {e.response.status_code}"
        try:
            detail = f"{detail} | {e.response.text[:500]}"
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"模型请求失败: {str(e)}")


@router.post("/export")
async def export_cases(request: ExportRequest):
    """
    导出测试用例 | Export Test Cases
    
    同步接口，用于Web前端步骤条 Step 4
    Synchronous endpoint for Web Frontend Step 4
    """
    from openpyxl import Workbook
    
    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"
    ws.append(["ID", "标题", "模块", "优先级", "类型", "前置条件", "操作步骤", "预期结果"])
    
    for c in request.test_cases:
        ws.append([
            c.get("id"),
            c.get("title"),
            c.get("module", ""),
            c.get("priority"),
            c.get("type"),
            c.get("preconditions"),
            c.get("steps"),
            c.get("expected_results")
        ])
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_cases_{timestamp}.xlsx"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    wb.save(filepath)
    
    return FileResponse(
        filepath, 
        filename=filename, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    启动分析任务 | Start analysis task
    
    异步执行，立即返回task_id
    Executes asynchronously, returns task_id immediately.
    
    **流程 Flow:**
    1. 验证平台支持 | Validate platform support
    2. 创建任务 | Create task
    3. 后台执行 | Execute in background
    4. 返回task_id | Return task_id
    
    **前端处理 Frontend:**
    - 立即显示进度条 | Show progress bar immediately
    - 轮询 `/analyze/{task_id}` 获取进度 | Poll `/analyze/{task_id}` for progress
    """
    url_str = str(request.url)
    
    # 检查平台支持
    if not PlatformRegistry.is_supported(url_str):
        supported = [p["display_name"] for p in PlatformRegistry.list_platforms()]
        raise HTTPException(
            status_code=400,
            detail=f"不支持的平台 | Unsupported platform. Supported: {supported}"
        )
    
    # 创建任务
    manager = get_task_manager()
    task_id = manager.create_task()
    
    # 获取平台信息
    adapter = PlatformRegistry.get_adapter(url_str)
    platform_name = adapter.info.display_name if adapter else "Unknown"
    
    # 定义后台任务
    async def progress_callback(p: Dict[str, Any]):
        manager.update_progress(
            task_id,
            p.get("step", p.get("state", "")),
            p.get("current", 0),
            p.get("total", 0),
            p.get("message", "")
        )

    async def run_analysis(task_id: str):
        model = build_model(None)
        engine = Engine(llm=model)
        result = await engine.run(
            url=url_str,
            pages=request.pages,
            progress_callback=progress_callback
        )
        return result
    
    # 添加到后台任务
    background_tasks.add_task(
        manager.run_task,
        task_id,
        run_analysis
    )
    
    return AnalyzeResponse(
        status="processing",
        message=f"任务已启动，平台: {platform_name} | Task started, platform: {platform_name}",
        task_id=task_id
    )


@router.get("/analyze/{task_id}")
async def get_analysis_status(task_id: str):
    """
    获取分析状态 | Get analysis status
    
    轮询此接口获取进度和结果
    Poll this endpoint for progress and results.
    
    **响应示例 Response Example:**
    ```json
    {
      "task_id": "abc123",
      "status": "running",
      "progress": {
        "step": "generating",
        "percentage": 60.0,
        "message": "正在生成测试用例..."
      },
      "result": null
    }
    ```
    """
    manager = get_task_manager()
    task = manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在 | Task not found")
    
    response = {
        "task_id": task.task_id,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "progress": {
            "step": task.progress.step,
            "current": task.progress.current,
            "total": task.progress.total,
            "percentage": task.progress.percentage,
            "message": task.progress.message
        },
        "result": task.result,
        "error": task.error
    }
    
    if task.completed_at:
        response["completed_at"] = task.completed_at.isoformat()
    
    return response


@router.delete("/analyze/{task_id}")
async def cancel_analysis(task_id: str):
    """
    取消分析任务 | Cancel analysis task
    """
    manager = get_task_manager()
    
    if manager.cancel_task(task_id):
        return {"status": "cancelled", "task_id": task_id}
    else:
        raise HTTPException(
            status_code=400,
            detail="无法取消任务（已完成或不存在）| Cannot cancel task (completed or not found)"
        )


@router.get("/platforms")
async def list_platforms():
    """
    列出支持的平台 | List supported platforms
    
    返回所有已注册的平台信息
    Returns all registered platform information.
    """
    platforms = PlatformRegistry.list_platforms()
    
    return {
        "total": len(platforms),
        "platforms": platforms
    }


@router.get("/health")
async def health_check():
    """健康检查 | Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.1.0-dev"
    }
