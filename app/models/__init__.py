"""
数据模型
"""

from app.core.schema import (
    ElementType,
    TestCasePriority,
    TestCaseType,
    UIElement,
    RequirementNode,
    TestCaseStep,
    TestCase,
    ExtractionResult,
    GenerationResult,
    ExportResult,
)
from .llm_config import (
    LLMProfile,
    LLMProfilesConfig,
    LLMProtocol,
    LLMProvider,
    AppConfig,
    UserSettings
)

__all__ = [
    # 核心数据模型
    "ElementType",
    "TestCasePriority",
    "TestCaseType",
    "UIElement",
    "RequirementNode",
    "TestCaseStep",
    "TestCase",
    "ExtractionResult",
    "GenerationResult",
    "ExportResult",
    # LLM 配置
    "LLMProfile",
    "LLMProfilesConfig",
    "LLMProtocol",
    "LLMProvider",
    # 应用配置
    "AppConfig",
    "UserSettings",
]