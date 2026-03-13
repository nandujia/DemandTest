<div align="center">

<img src="docs/images/logo.png" alt="智测AI Logo" width="200">

# 智测AI (Testify AI)

**基于多模态大模型的开源自动化测试工具**

**Open-Source Automated Testing Tool Powered by Multimodal LLM**

[!\[GitHub stars\](https://img.shields.io/github/stars/nandujia/DemandTest?style=social null)](https://github.com/nandujia/DemandTest/stargazers)
[!\[GitHub forks\](https://img.shields.io/github/forks/nandujia/DemandTest?style=social null)](https://github.com/nandujia/DemandTest/network/members)
[!\[GitHub watchers\](https://img.shields.io/github/watchers/nandujia/DemandTest?style=social null)](https://github.com/nandujia/DemandTest/watchers)

[!\[Version\](https://img.shields.io/badge/version-3.1.0--dev-orange.svg null)](https://github.com/nandujia/DemandTest/releases)
[!\[License\](https://img.shields.io/badge/license-MIT-green.svg null)](LICENSE)
[!\[Python\](https://img.shields.io/badge/python-3.11+-yellow.svg null)](https://www.python.org/)
[!\[Code style: black\](https://img.shields.io/badge/code%20style-black-000000.svg null)](https://github.com/psf/black)

[!\[GitHub Issues\](https://img.shields.io/github/issues/nandujia/DemandTest null)](https://github.com/nandujia/DemandTest/issues)
[!\[GitHub Pull Requests\](https://img.shields.io/github/issues-pr/nandujia/DemandTest null)](https://github.com/nandujia/DemandTest/pulls)
[!\[GitHub Contributors\](https://img.shields.io/github/contributors/nandujia/DemandTest null)](https://github.com/nandujia/DemandTest/graphs/contributors)

[!\[Test Status\](https://github.com/nandujia/DemandTest/workflows/Test%20and%20Lint/badge.svg null)](https://github.com/nandujia/DemandTest/actions)
[!\[Coverage Status\](https://codecov.io/gh/nandujia/DemandTest/branch/main/graph/badge.svg null)](https://codecov.io/gh/nandujia/DemandTest)

**[English](#-english-documentation)** **|** **[中文](#-中文文档)**

**[🚀 快速开始](#-快速开始)** **|** **[📖 文档](#-文档)** **|** **[🤝 贡献](#-贡献指南)** **|** **[💬 社区](#-社区)**

</div>

***

## 📖 中文文档

### 🎯 项目简介

**智测AI（Testify AI）** 是一款基于多模态大模型、通过chat（自然对话）从Axuer，墨刀，蓝湖等产研一体化平台提取需求，解析产品需求，生成对应测试用例，减轻测试工程师编写测试用例时间，提升整个团队效率。

> 💡 **核心理念**：让AI理解你的需求，自动生成专业的测试用例

**一行命令，从原型到测试用例**：

```bash
# 分析墨刀原型，自动生成测试用例
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://modao.cc/your-project"}'
```

***

### ✨ 核心特性

<table>
<tr>
<td width="50%">

#### 🔍 智能原型解析

- 支持**墨刀、蓝湖、Figma**等主流设计工具
- 协议级数据提取，绕过Canvas限制
- 自动识别页面结构、组件、交互逻辑

</td>
<td width="50%">

#### 🤖 AI测试生成

- 基于多模态大模型（GLM/GPT/Qwen）
- 自动生成正向、逆向、边界、异常测试
- 支持Few-Shot自学习，持续优化

</td>
</tr>
<tr>
<td width="50%">

#### 📊 结构化输出

- Pydantic保证**100%可解析**
- 支持Excel、JSON、Markdown多格式导出
- 可对接TestRail、Jira等测试管理平台

</td>
<td width="50%">

#### ⚡ 开箱即用

- 完整的RESTful API
- 支持Docker一键部署
- 插件化架构，易于扩展

</td>
</tr>
</table>

***

### 🚀 快速开始

#### 方式一：Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/nandujia/DemandTest.git
cd DemandTest

# 启动服务
docker-compose up -d

# 访问API文档
open http://localhost:8000/docs
```

#### 方式二：本地开发

```bash
# 1. 克隆项目
git clone https://github.com/nandujia/DemandTest.git
cd DemandTest

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，配置 LLM_API_KEY

# 4. 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 第一个测试用例

```python
import requests

# 1. 提交分析任务
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"url": "https://modao.cc/axbox/share/your-project"}
)
task_id = response.json()["task_id"]

# 2. 查询进度
import time
while True:
    status = requests.get(f"http://localhost:8000/api/v1/analyze/{task_id}").json()
    if status["status"] == "completed":
        print(f"生成测试用例: {len(status['result']['test_cases'])} 条")
        break
    time.sleep(2)
```

***

### 📊 效果展示

#### 从墨刀原型自动生成测试用例

**输入**：墨刀原型链接（97个页面）

**输出**：完整测试用例Excel文件

| 模块     | 测试用例数    | 覆盖场景     |
| ------ | -------- | -------- |
| 登录注册   | 4条       | 正向、逆向、边界 |
| VIP功能  | 32条      | 功能、安全、性能 |
| 充值提现   | 12条      | 业务流程、异常  |
| **总计** | **97+条** | 全面覆盖     |

***

### 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户请求                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│                   立即响应 + 后台任务                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Engine (编排引擎)                         │
│     Extractor → Generator (Few-Shot) → Exporter            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Platforms (平台插件)                        │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│   │  Modao   │ │  Lanhu   │ │  Figma   │ │  Axure   │     │
│   │   ✅     │ │   🚧    │ │   🚧    │ │   📋    │     │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│         策略模式 - 新增平台只需实现适配器接口                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Interceptor (数据嗅探引擎)                     │
│   Network Interception → 原始JSON → 隐藏字段 + 内部备注      │
└─────────────────────────────────────────────────────────────┘
```

***

### 📁 项目结构

```
testify-ai/
├── app/
│   ├── core/                   # 核心模块
│   │   ├── schema.py          # 数据模型 (Pydantic)
│   │   ├── engine.py          # 编排引擎
│   │   ├── config.py          # 配置管理
│   │   └── logging_config.py  # 日志系统
│   │
│   ├── platforms/              # 平台插件
│   │   ├── base.py            # 适配器基类
│   │   ├── registry.py        # 平台注册表
│   │   ├── modao/             # 墨刀适配器 ✅
│   │   ├── lanhu/             # 蓝湖适配器 🚧
│   │   └── figma/             # Figma适配器 🚧
│   │
│   ├── adapters/               # 数据嗅探
│   │   └── sniffer.py         # 网络拦截引擎
│   │
│   ├── services/               # 服务层
│   │   ├── async_tasks.py     # 异步任务管理
│   │   └── shadow_learning.py # 自学习服务
│   │
│   ├── utils/                  # 工具模块
│   │   └── security.py        # 安全工具
│   │
│   ├── llm/                    # LLM适配层
│   ├── api/                    # RESTful API
│   └── main.py                 # 应用入口
│
├── tests/                      # 单元测试
├── .github/workflows/          # CI/CD
├── docs/                       # 文档
└── exports/                    # 导出文件
```

***

### 📊 支持的平台

| 平台           | 状态     | 特性          |
| ------------ | ------ | ----------- |
| **墨刀 Modao** | ✅ 已支持  | 完整页面解析、组件提取 |
| **蓝湖 Lanhu** | 🚧 开发中 | 设计稿解析       |
| **Figma**    | 🚧 开发中 | 国际化设计工具     |
| **Axure**    | 📋 计划中 | 专业原型工具      |
| **即时设计**     | 📋 计划中 | 国产设计工具      |

**贡献新平台**：只需实现 `BasePlatformAdapter` 接口，详见 [贡献指南](CONTRIBUTING.md)

***

### 🔌 扩展开发

#### 添加新平台适配器

```python
# app/platforms/myplatform/adapter.py

from app.platforms.base import BasePlatformAdapter, PlatformInfo

class MyPlatformAdapter(BasePlatformAdapter):
    @property
    def info(self) -> PlatformInfo:
        return PlatformInfo(
            name="myplatform",
            display_name="我的平台",
            display_name_en="My Platform",
            url_patterns=["myplatform.com"]
        )
    
    def match(self, url: str) -> bool:
        return "myplatform.com" in url
    
    def get_sniff_patterns(self) -> dict:
        return {"api": ["/api/data"]}
    
    async def parse_sniffed_data(self, data):
        # 解析数据...
        return nodes

# 注册插件
from app.platforms.registry import PlatformRegistry
PlatformRegistry.register(MyPlatformAdapter)
```

***

### 🗺️ 路线图

- [x] v3.1.0 - 核心架构重构
  - [x] 插件化平台架构
  - [x] 协议级数据提取
  - [x] 异步任务系统
  - [x] 日志系统
  - [x] 安全模块
- [ ] v3.2.0 - 平台扩展
  - [ ] 蓝湖适配器
  - [ ] Figma适配器
  - [ ] 自定义平台插件市场
- [ ] v3.3.0 - 智能化增强
  - [ ] 多模态需求理解
  - [ ] 自动化测试执行
  - [ ] 缺陷预测
- [ ] v4.0.0 - 企业级特性
  - [ ] 团队协作
  - [ ] 测试报告生成
  - [ ] CI/CD集成

查看 [完整路线图](https://github.com/nandujia/DemandTest/milestones)

***

### 🤝 贡献指南

我们欢迎所有形式的贡献！

**贡献方式**：

- 🐛 [报告Bug](https://github.com/nandujia/DemandTest/issues/new?template=bug_report.md)
- 💡 [提出建议](https://github.com/nandujia/DemandTest/issues/new?template=feature_request.md)
- 📝 改进文档
- 🔧 提交代码

**贡献流程**：

```bash
# 1. Fork项目
# 2. 创建分支
git checkout -b feature/your-feature

# 3. 提交代码
git commit -m "feat: 添加XXX功能"

# 4. 推送并创建PR
git push origin feature/your-feature
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

***

### 👥 贡献者

感谢所有贡献者！

<a href="https://github.com/nandujia/DemandTest/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nandujia/DemandTest" />
</a>

***

### 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

***

### 💬 社区

- **GitHub Issues**: [提交问题](https://github.com/nandujia/DemandTest/issues)
- **GitHub Discussions**: [参与讨论](https://github.com/nandujia/DemandTest/discussions)
- **Discord**: [加入社区](https://discord.gg/clawd)

***

### ⭐ Star History

如果这个项目对你有帮助，请给我们一个 ⭐ Star！

[!\[Star History Chart\](https://api.star-history.com/svg?repos=nandujia/DemandTest\&type=Date null)](https://star-history.com/#nandujia/DemandTest\&Date)

***

<div align="center">

**Made with ❤️ by Testify AI Team**

**智测AI - 让测试更智能**

**[⭐ Star](https://github.com/nandujia/DemandTest)** **|** **[🍴 Fork](https://github.com/nandujia/DemandTest/fork)** **|** **[📖 文档](https://github.com/nandujia/DemandTest/wiki)**

</div>

***

## 📖 English Documentation

### 🎯 Overview

**Testify AI** is an **open-source automated testing tool** built on multimodal LLM, Agent intelligence, and plugin architecture.

> 💡 **Core Philosophy**: Let AI understand your requirements and automatically generate professional test cases

**One command from prototype to test cases**:

```bash
# Analyze Modao prototype, auto-generate test cases
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://modao.cc/your-project"}'
```

***

### ✨ Core Features

| Feature                        | Description                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------- |
| **🔍 Smart Prototype Parsing** | Support Modao, Lanhu, Figma; Protocol-level extraction bypassing Canvas limits   |
| **🤖 AI Test Generation**      | Multi-modal LLM (GLM/GPT/Qwen); Auto-generate positive, negative, boundary tests |
| **📊 Structured Output**       | 100% parseable with Pydantic; Export to Excel, JSON, Markdown                    |
| **⚡ Ready to Use**             | Complete RESTful API; Docker one-click deployment; Plugin architecture           |

***

### 🚀 Quick Start

```bash
# Clone
git clone https://github.com/nandujia/DemandTest.git

# Docker
docker-compose up -d

# Or local development
pip install -r requirements.txt
uvicorn app.main:app --reload
```

***

### 📊 Supported Platforms

| Platform | Status            |
| -------- | ----------------- |
| Modao    | ✅ Supported       |
| Lanhu    | 🚧 In Development |
| Figma    | 🚧 In Development |
| Axure    | 📋 Planned        |

***

### 🗺️ Roadmap

- [x] v3.1.0 - Core architecture refactor
- [ ] v3.2.0 - Platform expansion (Lanhu, Figma)
- [ ] v3.3.0 - AI enhancement
- [ ] v4.0.0 - Enterprise features

***

### 🤝 Contributing

We welcome all contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

***

### 📄 License

[MIT License](LICENSE)

***

<div align="center">

**[⭐ Star](https://github.com/nandujia/DemandTest)** **|** **[🍴 Fork](https://github.com/nandujia/DemandTest/fork)** **|** **[📖 Docs](https://github.com/nandujia/DemandTest/wiki)**

</div>
