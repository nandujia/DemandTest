# DemandTest Platform - 需求提取与测试用例生成平台

<div align="center">

**一款适配国内大部分产研平台的需求提取与测试用例生成工具**

自动爬取原型设计平台 → 提取需求目录 → 生成测试用例 → 导出 Excel

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)]()
[![Node](https://img.shields.io/badge/node-18+-green.svg)]()

</div>

---

## ✨ 功能特性

### 🔍 需求提取（Test_Demand）
- 🎯 **100% 覆盖** - API 监听方案，无需与 Canvas 较劲
- 🚀 **极速爬取** - 10 秒内获取完整页面列表
- 📋 **智能解析** - 自动解析原型目录结构
- ✅ **匹配验证** - 自动验证提取数量与显示数量

**支持平台：**
| 平台 | 覆盖率 | 状态 |
|------|--------|------|
| 墨刀 | 100% | ✅ |
| 蓝湖 | 100% | ✅ |
| Axure Share | 100% | ✅ |
| 幕客 | 100% | ✅ |
| Figma | 100% | ✅ |
| 即时设计 | 100% | ✅ |

### 📝 测试用例生成（Test_Case）
- 📊 **多类型覆盖** - 正向、逆向、边界、异常、安全、性能
- 📋 **标准格式** - 遵循行业标准测试用例模板
- 📥 **Excel 导出** - 一键导出，兼容 TestRail
- 🎯 **智能生成** - 根据需求自动生成测试用例

### 🖥️ 可视化界面
- 📦 **开箱即用** - Docker 一键部署
- 🎨 **简洁美观** - Vue 3 + Element Plus
- 📱 **响应式设计** - 支持桌面和移动端

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/nandujia/DemandTest.git
cd DemandTest

# 一键启动
docker-compose up -d

# 访问 http://localhost:8080
```

### 方式二：本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

---

## 📁 项目结构

```
demand-test-platform/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── crawler/       # 爬虫服务
│   │   │   ├── extractor/     # 需求提取
│   │   │   └── generator/     # 测试用例生成
│   │   ├── api/               # API 路由
│   │   └── utils/             # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端界面
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docs/                       # 文档
│   ├── API.md                 # API 文档
│   └── DEPLOYMENT.md          # 部署文档
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 📖 使用流程

```
1. 用户提交 URL → 2. 系统爬取原型 → 3. 提取目录结构
                                    ↓
6. 导出测试用例 ← 5. 生成测试用例 ← 4. 用户勾选需求
```

### 详细步骤

1. **提交 URL**
   - 在首页输入墨刀/蓝湖等平台分享链接
   - 系统自动识别平台类型

2. **爬取原型**
   - 系统通过 API 监听获取完整页面列表
   - 显示匹配率和爬取状态

3. **展示目录**
   - 以树形结构展示页面目录
   - 显示每个页面的状态（新增/修改）

4. **勾选需求**
   - 用户勾选需要生成测试用例的页面
   - 支持全选、批量选择

5. **生成测试用例**
   - 根据选中页面自动生成测试用例
   - 支持选择测试类型（正向/逆向/边界等）

6. **导出 Excel**
   - 一键导出为标准 Excel 格式
   - 兼容 TestRail 等测试管理系统

---

## 🔧 核心技术

### 需求提取算法

```
墨刀分享链接 → Playwright 监听 → 捕获 document.js → 解析 Axure 格式 → 提取页面名称
```

**核心代码：**
```python
# 从 .html 文件名提取页面名称
html_files = re.findall(r'"([^"]+\.html)"', document_content)
pages = [f.replace('.html', '') for f in html_files if not f.startswith('_')]
```

### 测试用例生成规则

| 输入 | 输出 |
|------|------|
| 页面名称 + 功能描述 | 正向测试用例 |
| 输入字段 + 约束条件 | 逆向/边界测试用例 |
| 业务规则 | 业务场景测试用例 |

**用例模板：**
| 字段 | 说明 |
|------|------|
| 用例编号 | TC_模块_序号 |
| 用例标题 | 类型-场景描述 |
| 前置条件 | 执行前必要条件 |
| 测试步骤 | 详细操作步骤 |
| 预期结果 | 每步预期输出 |
| 备注 | 优先级、依赖等 |

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 页面覆盖率 | 99%+ |
| 爬取速度 | <10s |
| 测试用例生成 | <5s/页 |
| 并发支持 | 10+ |

---

## 🛠️ API 文档

### 爬取原型
```http
POST /api/v1/crawl
Content-Type: application/json

{
  "url": "https://modao.cc/xxx"
}
```

### 生成测试用例
```http
POST /api/v1/generate
Content-Type: application/json

{
  "pages": ["登录", "注册"],
  "types": ["positive", "negative"]
}
```

### 导出 Excel
```http
GET /api/v1/export?format=xlsx
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

Made with ❤️ by nandujia

</div>
