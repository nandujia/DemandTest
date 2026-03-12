"""
核心模块 | Core Module

提供核心功能组件
Provides core functionality components.
"""

from .schema import (
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
from .logging_config import setup_logging, get_logger

__all__ = [
    # Schema
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
    # Logging
    "setup_logging",
    "get_logger",
]