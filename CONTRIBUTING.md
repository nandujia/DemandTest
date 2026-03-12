# 贡献指南

感谢您有兴趣为 DemandTest Platform 做出贡献！

## 🤝 如何贡献

### 1. Fork 仓库

点击页面右上角的 **Fork** 按钮，将仓库复制到你的账户下。

### 2. 克隆你的 Fork

```bash
git clone https://github.com/YOUR_USERNAME/DemandTest.git
cd DemandTest
```

### 3. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

### 4. 进行开发

```bash
# 安装依赖
pip install -r requirements.txt

# 创建配置文件
cp .env.example .env

# 运行开发服务器
uvicorn app.main:app --reload --port 8000
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: 添加XXX功能"
```

提交信息规范（Conventional Commits）：
- `feat:` 新功能
- `fix:` 修复Bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 6. 推送到你的 Fork

```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问你 Fork 的仓库页面
2. 点击 **Compare & pull request**
3. 填写 PR 标题和描述
4. 点击 **Create pull request**

---

## 📋 PR 检查清单

提交 PR 前，请确保：

- [ ] 代码符合项目的编码规范
- [ ] 已添加必要的测试
- [ ] 所有测试通过
- [ ] 已更新相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突

---

## 🐛 报告 Bug

如果你发现了 Bug，请创建 [Issue](https://github.com/nandujia/DemandTest/issues)，包含：

1. Bug 描述
2. 复现步骤
3. 期望行为
4. 实际行为
5. 环境信息（Python版本、操作系统等）

---

## 💡 提出新功能

如果你想提出新功能，请创建 [Issue](https://github.com/nandujia/DemandTest/issues)，包含：

1. 功能描述
2. 使用场景
3. 预期效果
4. 可选的实现思路

---

## 📝 代码规范

### Python 代码

- 遵循 PEP 8 规范
- 使用类型注解
- 添加必要的文档字符串
- 保持函数简洁（建议不超过50行）

### 文档

- 使用 Markdown 格式
- 中英文之间添加空格
- 代码块指定语言

---

## 🔍 代码审查

所有 PR 都需要经过审查才能合并。审查内容包括：

- 代码质量
- 功能完整性
- 测试覆盖率
- 文档完整性
- 性能影响

---

## 📜 许可证

提交代码即表示你同意你的贡献将根据 [MIT License](LICENSE) 授权。

---

## ❓ 问题？

如有问题，可以：
- 创建 [Issue](https://github.com/nandujia/DemandTest/issues)
- 发送邮件至：[你的邮箱]

感谢你的贡献！🙏
