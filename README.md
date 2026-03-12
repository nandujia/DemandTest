# DemandTest Platform

<div align="center">

**低侵入式产研数据转换器 | Non-Intrusive Product-Research Data Transformer**

**智能测试用例生成平台 | Intelligent Test Case Generation Platform**

[![Version](https://img.shields.io/badge/version-3.1.0--dev-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](#english) | [中文](#中文)

</div>

---

<a name="中文"></a>
## 📖 中文文档

### ⚠️ 开发状态 | Development Status

**当前版本 Current Version**: v3.1.0-dev

本项目正处于积极开发中，欢迎社区贡献！

This project is under active development. Community contributions are welcome!

---

### 🎯 项目定位 | Project Positioning

**DemandTest 是一款低侵入式产研数据转换器**

核心能力 | Core Capabilities:
1. **精准抓取**各大原型工具底层数据的拦截引擎
2. **结构化大模型**懂测试逻辑的测试用例生成
3. **自学习优化**持续改进的Few-Shot系统

---

### ✨ 核心特性 | Core Features

#### 🔍 协议级数据提取 | Protocol-Level Data Extraction

```
传统方案 Traditional Approach:
  DOM/OCR → 截图识别 → 易出错、Canvas无法解析

我们的方案 Our Approach:
  Network Interception → 拦截数据包 → 完美DOM、隐藏字段、内部备注
```

**优势 | Advantages:**
- ✅ 绕过Canvas渲染限制 | Bypass Canvas rendering limitations
- ✅ 获取隐藏字段和内部备注 | Extract hidden fields and internal notes
- ✅ 100%数据完整性 | 100% data integrity

#### 🤖 结构化LLM输出 | Structured LLM Output

```python
# Pydantic保证100%可解析
class TestCase(BaseModel):
    title: str
    steps: List[TestCaseStep]
    expected_result: str
```

**优势 | Advantages:**
- ✅ 类型安全 | Type safety
- ✅ 自动校验 | Automatic validation
- ✅ 无解析错误 | No parsing errors

#### 🧠 影子运行自学习 | Shadow Learning

```
用户修正 → 记录Prompt+Context → Few-Shot学习库 → 自动优化
```

**优势 | Advantages:**
- ✅ 记录用户修正 | Record user corrections
- ✅ 自动检索相似案例 | Auto-retrieve similar cases
- ✅ 持续质量提升 | Continuous quality improvement

#### ⚡ 全链路异步化 | Full Async Pipeline

```
API立即响应 → 后台任务执行 → 实时进度跟踪
```

**优势 | Advantages:**
- ✅ 非阻塞API | Non-blocking API
- ✅ 实时进度条 | Real-time progress bar
- ✅ 任务可取消 | Task cancellation

---

### 🏗️ 架构设计 | Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                    │
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
│   Modao | Lanhu | Figma | Axure | JSDesign | ...           │
│         策略模式 - 新增平台只需添加插件                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Interceptor (数据嗅探引擎)                     │
│   Network Interception → 原始JSON → 隐藏字段 + 内部备注      │
└─────────────────────────────────────────────────────────────┘
```

---

### 📁 项目结构 | Project Structure

```
demand-test-platform/
├── app/
│   ├── core/                   # 核心模块
│   │   ├── schema.py          # 数据模型
│   │   ├── engine.py          # 编排引擎
│   │   └── registry.py        # 平台注册表
│   │
│   ├── platforms/              # 平台插件
│   │   ├── base.py            # 适配器基类
│   │   ├── modao/             # 墨刀
│   │   ├── lanhu/             # 蓝湖
│   │   └── figma/             # Figma
│   │
│   ├── adapters/               # 数据嗅探
│   │   ├── sniffer.py         # 网络拦截引擎
│   │   └── base.py            # 适配器基类
│   │
│   ├── services/               # 服务层
│   │   ├── async_tasks.py     # 异步任务管理
│   │   └── shadow_learning.py # 自学习服务
│   │
│   ├── llm/                    # LLM适配层
│   ├── api/                    # API接口
│   └── main.py                 # 入口
│
├── data/                       # 数据存储
│   ├── learning/              # 学习数据
│   ├── tasks/                 # 任务结果
│   └── sniffed/               # 嗅探数据
│
├── exports/                    # 导出文件
└── docs/                       # 文档
    ├── REFACTOR_v3.1.md       # 重构方案
    └── CODE_REVIEW.md         # 代码审查
```

---

### 🚀 快速开始 | Quick Start

#### 本地开发 | Local Development

```bash
# 克隆仓库 Clone repository
git clone https://github.com/nandujia/DemandTest.git
cd DemandTest

# 安装依赖 Install dependencies
pip install -r requirements.txt

# 配置环境变量 Configure environment
cp .env.example .env
# 编辑 .env 配置 LLM_API_KEY

# 启动开发服务器 Start development server
uvicorn app.main:app --reload --port 8000
```

#### Docker部署 | Docker Deployment

```bash
docker-compose up -d
# 访问 http://localhost:8000
```

---

### 🤝 贡献指南 | Contributing

我们欢迎所有形式的贡献！| We welcome all forms of contributions!

#### 协作模式 | Collaboration Model

本项目采用 **Fork + Pull Request** 模式：

```
你的主仓库 (main) → 受保护，只接受PR
     ↑
  Pull Request (需要审核)
     ↑
贡献者的Fork仓库 → 开发 → 提交PR
```

#### 如何贡献 | How to Contribute

```bash
# 1. Fork仓库到你的账户

# 2. 克隆你的Fork
git clone https://github.com/YOUR_USERNAME/DemandTest.git

# 3. 创建功能分支
git checkout -b feature/your-feature

# 4. 提交变更
git commit -m "feat: 添加XXX功能"

# 5. 推送并创建PR
git push origin feature/your-feature
```

详细指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

### 🔐 数据隐私 | Data Privacy

#### 数据安全原则 | Data Security Principles

| 原则 | 说明 |
|------|------|
| **最小权限** | 仅请求必要的API权限 |
| **本地存储** | 所有数据存储在本地，不上传云端 |
| **敏感过滤** | 自动过滤敏感字段（密钥、密码等） |
| **审计日志** | 记录所有数据访问操作 |

#### 数据存储位置 | Data Storage Locations

```
./data/
├── learning/     # 学习数据（本地）
├── tasks/        # 任务结果（本地）
├── sniffed/      # 嗅探数据（本地）
└── config/       # 配置文件（本地）

./exports/        # 导出文件（本地）
```

#### 隐私建议 | Privacy Recommendations

1. **不要提交敏感数据** | Don't commit sensitive data
   - 添加 `.env` 到 `.gitignore`
   - 使用环境变量管理API密钥

2. **定期清理数据** | Regularly clean data
   ```bash
   rm -rf ./data/sniffed/*
   rm -rf ./data/tasks/*
   ```

3. **使用私有仓库** | Use private repositories
   - 敏感项目建议使用私有Fork

---

### 📊 支持的平台 | Supported Platforms

| 平台 Platform | 状态 Status | 说明 Description |
|---------------|-------------|------------------|
| 墨刀 Modao | ✅ 开发中 | 国产原型设计工具 |
| 蓝湖 Lanhu | 🚧 计划中 | 设计协作平台 |
| Figma | 🚧 计划中 | 在线设计工具 |
| Axure | 🚧 计划中 | 专业原型工具 |
| 即时设计 JSDesign | 🚧 计划中 | 国产设计工具 |

**新增平台**：只需实现 `BasePlatformAdapter`，无需修改核心代码！

---

### 📝 许可证 | License

[MIT License](LICENSE)

---

<a name="english"></a>
## 📖 English Documentation

### ⚠️ Development Status

**Current Version**: v3.1.0-dev

This project is under active development. Community contributions are welcome!

---

### 🎯 Project Positioning

**DemandTest is a non-intrusive product-research data transformer.**

Core Capabilities:
1. **Precise interception engine** that captures underlying data from prototyping tools
2. **Structured LLM** that understands testing logic for test case generation
3. **Self-learning optimization** with continuous Few-Shot improvements

---

### ✨ Core Features

#### 🔍 Protocol-Level Data Extraction

```
Traditional Approach:
  DOM/OCR → Screenshot Recognition → Error-prone, Canvas unparsable

Our Approach:
  Network Interception → Intercept Data Packets → Perfect DOM, hidden fields, internal notes
```

**Advantages:**
- ✅ Bypass Canvas rendering limitations
- ✅ Extract hidden fields and internal notes
- ✅ 100% data integrity

#### 🤖 Structured LLM Output

```python
# Pydantic ensures 100% parseability
class TestCase(BaseModel):
    title: str
    steps: List[TestCaseStep]
    expected_result: str
```

**Advantages:**
- ✅ Type safety
- ✅ Automatic validation
- ✅ No parsing errors

#### 🧠 Shadow Learning

```
User Correction → Record Prompt+Context → Few-Shot Library → Auto Optimization
```

**Advantages:**
- ✅ Record user corrections
- ✅ Auto-retrieve similar cases
- ✅ Continuous quality improvement

#### ⚡ Full Async Pipeline

```
Immediate API Response → Background Task Execution → Real-time Progress Tracking
```

**Advantages:**
- ✅ Non-blocking API
- ✅ Real-time progress bar
- ✅ Task cancellation support

---

### 🚀 Quick Start

#### Local Development

```bash
# Clone repository
git clone https://github.com/nandujia/DemandTest.git
cd DemandTest

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to configure LLM_API_KEY

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Docker Deployment

```bash
docker-compose up -d
# Access at http://localhost:8000
```

---

### 🤝 Contributing

We welcome all forms of contributions!

#### Collaboration Model

This project uses the **Fork + Pull Request** model:

```
Your Main Repository (main) → Protected, only accepts PRs
     ↑
  Pull Request (requires review)
     ↑
Contributor's Fork Repository → Development → Submit PR
```

#### How to Contribute

```bash
# 1. Fork the repository to your account

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/DemandTest.git

# 3. Create a feature branch
git checkout -b feature/your-feature

# 4. Commit changes
git commit -m "feat: add XXX feature"

# 5. Push and create PR
git push origin feature/your-feature
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

### 🔐 Data Privacy

#### Data Security Principles

| Principle | Description |
|-----------|-------------|
| **Least Privilege** | Only request necessary API permissions |
| **Local Storage** | All data stored locally, not uploaded to cloud |
| **Sensitive Filtering** | Auto-filter sensitive fields (keys, passwords) |
| **Audit Logging** | Record all data access operations |

#### Data Storage Locations

```
./data/
├── learning/     # Learning data (local)
├── tasks/        # Task results (local)
├── sniffed/      # Sniffed data (local)
└── config/       # Configuration (local)

./exports/        # Export files (local)
```

#### Privacy Recommendations

1. **Don't commit sensitive data**
   - Add `.env` to `.gitignore`
   - Use environment variables for API keys

2. **Regularly clean data**
   ```bash
   rm -rf ./data/sniffed/*
   rm -rf ./data/tasks/*
   ```

3. **Use private repositories**
   - For sensitive projects, use a private fork

---

### 📊 Supported Platforms

| Platform | Status | Description |
|----------|--------|-------------|
| Modao | ✅ In Development | Chinese prototyping tool |
| Lanhu | 🚧 Planned | Design collaboration platform |
| Figma | 🚧 Planned | Online design tool |
| Axure | 🚧 Planned | Professional prototyping tool |
| JSDesign | 🚧 Planned | Chinese design tool |

**Adding Platforms**: Simply implement `BasePlatformAdapter`, no core code changes needed!

---

### 📝 License

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ by DemandTest Team**

[GitHub](https://github.com/nandujia/DemandTest) | [Issues](https://github.com/nandujia/DemandTest/issues) | [Discussions](https://github.com/nandujia/DemandTest/discussions)

</div>
