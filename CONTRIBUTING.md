# 贡献指南 | Contributing Guide

感谢你对 PayGuard Crew 项目的关注！我们欢迎各种形式的贡献。

[English](#english) | [简体中文](#简体中文)

---

## 简体中文

### 🤝 如何贡献

我们欢迎以下类型的贡献：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复或新功能
- 🌍 翻译文档
- ⭐ 分享和推广项目

### 📋 贡献流程

#### 1. 报告问题

如果你发现了 Bug 或有功能建议：

1. 检查 [Issues](https://github.com/pocheang/payguard-crew/issues) 是否已有类似问题
2. 如果没有，创建新 Issue，请包含：
   - 清晰的标题
   - 详细的描述
   - 复现步骤（如果是 Bug）
   - 预期行为 vs 实际行为
   - 环境信息（Python 版本、操作系统等）
   - 相关日志或截图

#### 2. 提交代码

##### 开发环境设置

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/your-username/payguard-crew.git
cd payguard-crew

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖（如果有）

# 4. 初始化数据库
python -m app.db.database

# 5. 运行测试确保环境正常
python -m pytest tests/  # 如果有测试
```

##### 开发工作流

```bash
# 1. 创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix

# 2. 进行开发
# 编写代码...

# 3. 运行测试
python -m pytest tests/

# 4. 提交更改
git add .
git commit -m "feat: add your feature description"
# 或
git commit -m "fix: fix bug description"

# 5. 推送到你的 Fork
git push origin feature/your-feature-name

# 6. 在 GitHub 上创建 Pull Request
```

### 📐 代码规范

#### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（既不是新功能也不是修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```bash
feat(agent): add new fraud detection rules

- Add velocity check for high-risk countries
- Implement device fingerprint validation
- Update risk scoring algorithm

Closes #123
```

#### Python 代码规范

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 4 个空格缩进
- 函数和类添加文档字符串
- 变量和函数使用描述性命名
- 单行长度不超过 100 字符

```python
def calculate_risk_score(transaction: dict) -> float:
    """
    计算交易风险评分
    
    Args:
        transaction: 交易数据字典
        
    Returns:
        风险评分 (0.0-1.0)
    """
    # 实现...
    pass
```

#### 文件组织

- 新增 Agent 放在 `app/agents/prompts/` 目录
- 新增规则放在 `app/rules/` 目录
- 工具函数放在 `app/utils/` 目录
- 测试文件放在 `tests/` 目录，与源文件结构对应

### 🧪 测试要求

- 新功能必须包含测试
- Bug 修复应包含回归测试
- 确保所有测试通过
- 保持代码覆盖率不降低

```bash
# 运行测试
python -m pytest tests/

# 查看覆盖率
python -m pytest --cov=app tests/
```

### 📝 文档要求

- 新功能需要更新相关文档
- API 更改需要更新 README.md
- 重大更新需要在 CHANGELOG.md 中记录
- 代码注释使用中文或英文（保持一致）

### 🔍 Pull Request 检查清单

在提交 PR 之前，请确认：

- [ ] 代码遵循项目规范
- [ ] 已添加必要的测试
- [ ] 所有测试通过
- [ ] 已更新相关文档
- [ ] 提交信息符合规范
- [ ] PR 描述清晰完整
- [ ] 已解决所有冲突

### 📋 Pull Request 模板

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 性能优化

## 变更说明
<!-- 简要描述你的更改 -->

## 相关 Issue
<!-- 关联的 Issue 编号，例如：Closes #123 -->

## 测试说明
<!-- 如何测试这些更改 -->

## 截图（如适用）
<!-- 如果有 UI 变更，请添加截图 -->

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已添加/更新测试
- [ ] 所有测试通过
- [ ] 已更新文档
```

### 🎯 贡献重点领域

我们特别欢迎以下方面的贡献：

1. **风险检测规则**
   - 新的欺诈检测模式
   - 改进现有规则准确性
   - 减少误报率

2. **合规标准**
   - 新增国际监管标准支持
   - 更新现有合规检查逻辑
   - 合规文档完善

3. **性能优化**
   - 数据库查询优化
   - Agent 执行效率提升
   - 并发处理改进

4. **文档改进**
   - 使用示例
   - 最佳实践指南
   - 多语言翻译

5. **测试覆盖**
   - 单元测试
   - 集成测试
   - 边界情况测试

### 🌟 成为贡献者

一旦你的 PR 被合并，你将：

- 在 README.md 的贡献者列表中被提及
- 获得项目徽章（如果适用）
- 成为 PayGuard Crew 社区的一员

### 📧 联系方式

如有问题，可以通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/pocheang/payguard-crew/issues)
- GitHub Discussions: [参与讨论](https://github.com/pocheang/payguard-crew/discussions)

### 📜 行为准则

参与本项目即表示你同意遵守我们的行为准则：

- 尊重所有贡献者
- 保持专业和友善
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## English

### 🤝 How to Contribute

We welcome contributions in the following forms:

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit code fixes or new features
- 🌍 Translate documentation
- ⭐ Share and promote the project

### 📋 Contribution Process

#### 1. Report Issues

If you find a bug or have a feature suggestion:

1. Check existing [Issues](https://github.com/pocheang/payguard-crew/issues)
2. If not found, create a new Issue including:
   - Clear title
   - Detailed description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment info (Python version, OS, etc.)
   - Related logs or screenshots

#### 2. Submit Code

##### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/payguard-crew.git
cd payguard-crew

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# 4. Initialize database
python -m app.db.database

# 5. Run tests to ensure setup
python -m pytest tests/  # If available
```

##### Development Workflow

```bash
# 1. Create a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix

# 2. Make your changes
# Write code...

# 3. Run tests
python -m pytest tests/

# 4. Commit changes
git add .
git commit -m "feat: add your feature description"
# or
git commit -m "fix: fix bug description"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
```

### 📐 Code Standards

#### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation updates
- `style`: Code formatting (no functional change)
- `refactor`: Code refactoring
- `perf`: Performance optimization
- `test`: Test related
- `chore`: Build process or tool changes

**Example:**
```bash
feat(agent): add new fraud detection rules

- Add velocity check for high-risk countries
- Implement device fingerprint validation
- Update risk scoring algorithm

Closes #123
```

#### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Add docstrings to functions and classes
- Use descriptive naming
- Max line length: 100 characters

```python
def calculate_risk_score(transaction: dict) -> float:
    """
    Calculate transaction risk score
    
    Args:
        transaction: Transaction data dictionary
        
    Returns:
        Risk score (0.0-1.0)
    """
    # Implementation...
    pass
```

### 🧪 Testing Requirements

- New features must include tests
- Bug fixes should include regression tests
- Ensure all tests pass
- Maintain code coverage

```bash
# Run tests
python -m pytest tests/

# Check coverage
python -m pytest --cov=app tests/
```

### 📝 Documentation Requirements

- Update relevant documentation for new features
- Update README.md for API changes
- Record major updates in CHANGELOG.md
- Use consistent language in comments

### 🔍 Pull Request Checklist

Before submitting a PR:

- [ ] Code follows project standards
- [ ] Tests added for new features
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] PR description is clear
- [ ] All conflicts resolved

### 🎯 Focus Areas

We especially welcome contributions in:

1. **Risk Detection Rules**
   - New fraud detection patterns
   - Improve existing rule accuracy
   - Reduce false positives

2. **Compliance Standards**
   - Add international regulatory standards
   - Update compliance checking logic
   - Enhance compliance documentation

3. **Performance Optimization**
   - Database query optimization
   - Agent execution efficiency
   - Concurrency improvements

4. **Documentation**
   - Usage examples
   - Best practice guides
   - Multi-language translations

5. **Test Coverage**
   - Unit tests
   - Integration tests
   - Edge case testing

### 🌟 Become a Contributor

Once your PR is merged, you will:

- Be listed in the contributors section of README.md
- Receive project badges (if applicable)
- Become part of the PayGuard Crew community

### 📧 Contact

For questions, reach out via:

- GitHub Issues: [Submit an issue](https://github.com/pocheang/payguard-crew/issues)
- GitHub Discussions: [Join discussions](https://github.com/pocheang/payguard-crew/discussions)

### 📜 Code of Conduct

By participating, you agree to:

- Respect all contributors
- Be professional and friendly
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

---

## 🙏 致谢 | Acknowledgments

感谢所有为 PayGuard Crew 做出贡献的开发者！

Thank you to all contributors who help make PayGuard Crew better!

---

**许可证 | License**: MIT

**项目地址 | Repository**: https://github.com/pocheang/payguard-crew
