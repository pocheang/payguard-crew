# 贡献指南

感谢你对PayGuard项目的关注！本文档将指导你如何为项目做出贡献。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request流程](#pull-request流程)
- [问题报告](#问题报告)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

### 不可接受的行为

- ❌ 使用性别化的语言或图像
- ❌ 侮辱性/贬损性评论和人身攻击
- ❌ 公开或私下骚扰
- ❌ 未经许可发布他人的私人信息

---

## 如何贡献

### 贡献方式

你可以通过以下方式为项目做出贡献：

1. **报告Bug** - 发现问题？请告诉我们
2. **建议新功能** - 有好的想法？欢迎分享
3. **改进文档** - 文档永远可以更好
4. **提交代码** - 修复bug或实现新功能
5. **代码审查** - 帮助审查其他人的PR

### 贡献类型

#### 🐛 Bug修复
适合新手！查找标记为 `good first issue` 的问题。

#### ✨ 新功能
请先开启Discussion讨论，确认功能方向后再开始开发。

#### 📝 文档改进
文档改进不需要讨论，直接提交PR即可。

#### 🧪 测试增强
增加测试覆盖率，帮助提高代码质量。

---

## 开发环境设置

### 前置要求

- Python 3.11+
- Node.js 16+
- Git
- Docker（可选）

### 步骤

1. **Fork 仓库**

点击GitHub页面右上角的"Fork"按钮。

2. **克隆你的Fork**

```bash
git clone https://github.com/YOUR_USERNAME/payguard.git
cd payguard
```

3. **添加上游仓库**

```bash
git remote add upstream https://github.com/original/payguard.git
```

4. **创建开发分支**

```bash
git checkout -b feature/your-feature-name
```

5. **安装依赖**

```bash
# 后端
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 前端
cd frontend
npm install
```

6. **配置环境**

```bash
cp .env.example .env
# 编辑 .env 配置开发环境
```

7. **运行开发服务器**

```bash
# 后端
uvicorn app.main:app --reload

# 前端（新终端）
cd frontend && npm run dev
```

---

## 代码规范

### Python代码规范

遵循 [PEP 8](https://pep8.org/) 风格指南。

```bash
# 安装工具
pip install black flake8 isort

# 格式化代码
black app/
isort app/

# 检查代码
flake8 app/
```

#### 示例

```python
# ✅ 好的实践
def audit_transaction(tx: Transaction) -> AuditResult:
    """
    审计交易

    Args:
        tx: 交易数据

    Returns:
        审计结果
    """
    pass

# ❌ 避免
def audit(tx):  # 缺少类型提示和文档
    pass
```

### JavaScript代码规范

遵循 [Airbnb Style Guide](https://github.com/airbnb/javascript)。

```bash
# 安装工具
npm install --save-dev eslint prettier

# 格式化代码
npm run lint:fix

# 检查代码
npm run lint
```

#### 示例

```javascript
// ✅ 好的实践
export function auditTransaction(tx) {
  // 清晰的函数名和参数
}

// ❌ 避免
export function audit(t) {  // 名称过于简短
  console.log(t)  // 生产代码中不应有console.log
}
```

### 通用规范

1. **命名规范**
   - 使用有意义的变量名
   - 函数名使用动词开头
   - 类名使用名词，首字母大写

2. **注释规范**
   - 公共API必须有文档字符串
   - 复杂逻辑添加注释解释
   - 避免显而易见的注释

3. **代码组织**
   - 遵循[代码组织指南](docs/guides/CODE_ORGANIZATION_GUIDE.md)
   - 单一职责原则
   - 保持函数简短（< 50行）

---

## 提交规范

### Commit Message格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```bash
# 好的提交消息
feat(api): add batch audit endpoint
fix(frontend): resolve dashboard chart loading issue
docs(readme): update installation instructions

# 避免的提交消息
update code
fix bug
changes
```

---

## Pull Request流程

### 提交PR前

- [ ] 代码遵循项目规范
- [ ] 所有测试通过
- [ ] 添加了新测试（如适用）
- [ ] 更新了相关文档
- [ ] Commit消息符合规范
- [ ] 代码经过格式化

### 提交步骤

1. **确保分支最新**

```bash
git fetch upstream
git rebase upstream/main
```

2. **推送到你的Fork**

```bash
git push origin feature/your-feature-name
```

3. **创建Pull Request**

- 访问GitHub上你的Fork
- 点击 "New Pull Request"
- 填写PR模板

### PR标题格式

```
[Type] Brief description

例如：
[Feature] Add WebSocket real-time notifications
[Fix] Resolve dashboard loading timeout
[Docs] Update API documentation
```

### PR描述模板

```markdown
## 🎯 目的
简要说明这个PR要解决什么问题

## 📝 改动内容
- 改动点1
- 改动点2

## 🧪 测试
说明如何测试这些改动

## 📷 截图（如适用）
添加截图展示UI改动

## ✅ 检查清单
- [ ] 代码遵循项目规范
- [ ] 所有测试通过
- [ ] 添加了新测试
- [ ] 更新了文档
```

### PR审查

- 至少需要1个维护者批准
- 所有CI检查必须通过
- 没有合并冲突
- 代码审查反馈已解决

---

## 问题报告

### Bug报告

使用Bug报告模板，包含：

```markdown
## 🐛 Bug描述
清晰简洁地描述bug

## 📋 复现步骤
1. 访问 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## ✅ 期望行为
描述你期望发生什么

## 📷 截图
如果适用，添加截图

## 🖥️ 环境
- OS: [例如 Windows 11]
- Python版本: [例如 3.11]
- 浏览器: [例如 Chrome 120]

## 📝 附加信息
其他相关信息
```

### 功能请求

使用功能请求模板，包含：

```markdown
## 🚀 功能描述
清晰简洁地描述功能

## 💡 动机
为什么需要这个功能？解决什么问题？

## 📋 建议方案
如何实现这个功能

## 🔄 替代方案
考虑过的其他方案

## 📝 附加信息
其他相关信息
```

---

## 测试指南

### 运行测试

```bash
# 所有测试
pytest

# 特定测试
pytest tests/api/test_audit.py -v

# 覆盖率
pytest --cov=app --cov-report=html
```

### 编写测试

```python
def test_audit_transaction_success():
    """测试: 成功审计交易"""
    response = client.post(
        "/api/audit/transaction",
        headers={"X-API-Key": "test-key"},
        json={"transaction_id": "TX001", "amount": 1000}
    )
    
    assert response.status_code == 200
    assert "risk_score" in response.json()
```

---

## 获取帮助

### 联系方式

- 💬 GitHub Discussions - 一般讨论
- 🐛 GitHub Issues - Bug报告和功能请求
- 📧 Email - support@payguard.com

### 有用资源

- [文档中心](docs/README.md)
- [代码组织指南](docs/guides/CODE_ORGANIZATION_GUIDE.md)
- [快速参考](docs/guides/QUICK_REFERENCE.md)

---

## 版本发布

维护者发布新版本的流程：

1. 更新 `CHANGELOG.md`
2. 更新版本号
3. 创建Git标签
4. 推送到GitHub
5. 创建GitHub Release

---

## 感谢贡献者

感谢所有为PayGuard做出贡献的开发者！

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- 贡献者列表 -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

---

## 许可证

贡献到本项目即表示你同意你的贡献将按照项目的 [MIT License](LICENSE) 进行许可。

---

**再次感谢你的贡献！** 🎉

如有任何问题，欢迎随时联系维护团队。
