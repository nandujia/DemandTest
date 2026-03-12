"""
全局数据模型定义
Global Schema Definitions

使用Pydantic保证类型安全和LLM输出的100%可解析性
Using Pydantic ensures type safety and 100% parseability of LLM outputs.

设计原则 Design Principles:
1. 标准化：所有平台输出统一格式
2. 类型安全：使用Pydantic强制校验
3. 可扩展：支持任意平台的数据结构
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============ 枚举定义 Enum Definitions ============

class ElementType(str, Enum):
    """UI元素类型 UI Element Types"""
    BUTTON = "button"
    INPUT = "input"
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    CONTAINER = "container"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    UNKNOWN = "unknown"


class TestCasePriority(str, Enum):
    """测试用例优先级 Test Case Priority"""
    P0 = "P0"  # 阻塞性 Blocker
    P1 = "P1"  # 严重 Critical
    P2 = "P2"  # 一般 Major
    P3 = "P3"  # 次要 Minor


class TestCaseType(str, Enum):
    """测试用例类型 Test Case Types"""
    POSITIVE = "positive"      # 正向测试 Positive testing
    NEGATIVE = "negative"      # 逆向测试 Negative testing
    BOUNDARY = "boundary"      # 边界测试 Boundary testing
    EXCEPTION = "exception"    # 异常测试 Exception testing
    SECURITY = "security"      # 安全测试 Security testing
    COMPATIBILITY = "compatibility"  # 兼容性测试 Compatibility testing


# ============ UI元素模型 UI Element Models ============

class UIElement(BaseModel):
    """
    UI元素
    UI Element
    
    代表页面上的一个可交互元素
    Represents an interactive element on a page.
    """
    id: str = Field(..., description="元素ID Element ID")
    type: ElementType = Field(default=ElementType.UNKNOWN, description="元素类型 Element type")
    name: Optional[str] = Field(None, description="元素名称 Element name")
    text: Optional[str] = Field(None, description="显示文本 Display text")
    selector: Optional[str] = Field(None, description="CSS选择器 CSS selector")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="其他属性 Other attributes")
    children: List["UIElement"] = Field(default_factory=list, description="子元素 Child elements")
    
    class Config:
        use_enum_values = True


# ============ 需求节点模型 Requirement Node Models ============

class RequirementNode(BaseModel):
    """
    需求节点 - 标准格式
    Requirement Node - Standard Format
    
    解耦平台差异，提供统一的需求表示
    Decouples platform differences, provides unified requirement representation.
    """
    id: str = Field(..., description="节点ID Node ID")
    name: str = Field(..., description="页面/功能名称 Page/Feature name")
    page_id: str = Field(default="", description="页面ID Page ID")
    url: Optional[str] = Field(None, description="页面URL Page URL")
    description: Optional[str] = Field(None, description="功能描述 Feature description")
    elements: List[UIElement] = Field(default_factory=list, description="UI元素列表 UI element list")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始数据 Raw data")
    screenshot_path: Optional[str] = Field(None, description="截图路径 Screenshot path")
    
    def to_prompt_text(self) -> str:
        """转换为Prompt文本 Convert to prompt text"""
        lines = [
            f"页面名称: {self.name}",
            f"页面ID: {self.page_id}",
        ]
        if self.description:
            lines.append(f"功能描述: {self.description}")
        if self.elements:
            lines.append(f"元素数量: {len(self.elements)}")
            for elem in self.elements[:10]:  # 只展示前10个
                if elem.name or elem.text:
                    lines.append(f"  - {elem.type}: {elem.name or elem.text}")
        return "\n".join(lines)


# ============ 测试用例模型 Test Case Models ============

class TestCaseStep(BaseModel):
    """
    测试步骤
    Test Case Step
    
    单个测试操作步骤
    Single test operation step.
    """
    order: int = Field(..., description="步骤序号 Step order")
    action: str = Field(..., description="操作描述 Action description")
    target: Optional[str] = Field(None, description="目标元素 Target element")
    value: Optional[str] = Field(None, description="输入值 Input value")
    expected: Optional[str] = Field(None, description="预期结果 Expected result")


class TestCase(BaseModel):
    """
    测试用例
    Test Case
    
    完整的测试用例定义
    Complete test case definition.
    """
    id: str = Field(..., description="用例ID Case ID")
    title: str = Field(..., description="用例标题 Case title")
    module: Optional[str] = Field(None, description="所属模块 Module")
    priority: TestCasePriority = Field(
        default=TestCasePriority.P2, 
        description="优先级 Priority"
    )
    type: TestCaseType = Field(
        default=TestCaseType.POSITIVE, 
        description="用例类型 Case type"
    )
    preconditions: List[str] = Field(
        default_factory=list, 
        description="前置条件 Preconditions"
    )
    steps: List[TestCaseStep] = Field(
        default_factory=list, 
        description="操作步骤 Steps"
    )
    expected_result: str = Field(..., description="预期结果 Expected result")
    tags: List[str] = Field(default_factory=list, description="标签 Tags")
    
    class Config:
        use_enum_values = True


# ============ 提取结果模型 Extraction Result Models ============

class ExtractionResult(BaseModel):
    """
    提取结果
    Extraction Result
    
    数据嗅探和解析的结果
    Result of data sniffing and parsing.
    """
    platform: str = Field(..., description="平台名称 Platform name")
    url: str = Field(..., description="来源URL Source URL")
    pages: List[RequirementNode] = Field(
        default_factory=list, 
        description="页面列表 Page list"
    )
    total_elements: int = Field(default=0, description="元素总数 Total elements")
    success: bool = Field(default=True, description="是否成功 Success flag")
    error: Optional[str] = Field(None, description="错误信息 Error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据 Metadata")


class GenerationResult(BaseModel):
    """
    生成结果
    Generation Result
    
    测试用例生成的结果
    Result of test case generation.
    """
    page_name: str = Field(..., description="页面名称 Page name")
    test_cases: List[TestCase] = Field(
        default_factory=list, 
        description="测试用例列表 Test case list"
    )
    total: int = Field(default=0, description="用例总数 Total cases")
    success: bool = Field(default=True, description="是否成功 Success flag")
    error: Optional[str] = Field(None, description="错误信息 Error message")
    enhanced_prompt: Optional[str] = Field(None, description="增强后的Prompt Enhanced prompt")


# ============ 导出结果模型 Export Result Models ============

class ExportResult(BaseModel):
    """
    导出结果
    Export Result
    
    文件导出的结果
    Result of file export.
    """
    file_path: str = Field(..., description="文件路径 File path")
    format: str = Field(default="xlsx", description="文件格式 File format")
    success: bool = Field(default=True, description="是否成功 Success flag")
    error: Optional[str] = Field(None, description="错误信息 Error message")
