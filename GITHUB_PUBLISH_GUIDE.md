# 📤 GitHub 发布指南

**项目**: PayGuard Crew  
**版本**: 0.1.0  
**日期**: 2026-06-24

---

## ✅ 可以上传到 GitHub 的文件

### 📚 文档类（11个）

#### 核心文档
- ✅ **README.md** - 项目主文档（必须）
- ✅ **PAYGUARD_CREW_DEV.md** - 开发设计文档
- ✅ **CHANGELOG.md** - 版本变更历史
- ✅ **DOCS_INDEX.md** - 文档索引
- ✅ **VERSION.txt** - 版本号
- ✅ **DOCUMENTATION_CLEANUP_REPORT.md** - 整理报告
- ✅ **GITHUB_PUBLISH_GUIDE.md** - 本文档

#### 业务文档（知识库）
- ✅ **docs/kyc_policy.md** - KYC 政策
- ✅ **docs/aml_review_guide.md** - AML 指南
- ✅ **docs/payment_risk_rules.md** - 风险规则
- ✅ **docs/merchant_risk_policy.md** - 商户政策
- ✅ **docs/manual_review_process.md** - 复核流程
- ✅ **docs/api_documentation.md** - API 文档

### 💻 代码文件（全部）

#### 应用代码
- ✅ **app/** - 所有应用代码
  - app/main.py
  - app/config.py
  - app/agents/
  - app/api/
  - app/auth/
  - app/crew/
  - app/db/
  - app/middleware/
  - app/rag/
  - app/rules/
  - app/schemas/
  - app/utils/

#### 测试代码
- ✅ **tests/** - 所有测试文件
  - test_api.py
  - test_config.py
  - test_db.py
  - test_monitoring.py
  - test_performance.py
  - test_rag.py
  - test_retriever.py
  - test_rules.py
  - test_security.py
  - conftest.py

#### 脚本
- ✅ **scripts/** - 工具脚本
  - ingest_docs.py
  - quick-fix.sh
  - quick-fix.ps1

### 📦 配置文件

- ✅ **requirements.txt** - Python 依赖
- ✅ **requirements-dev.txt** - 开发依赖
- ✅ **pyproject.toml** - 工具配置
- ✅ **pytest.ini** - Pytest 配置
- ✅ **Dockerfile** - Docker 配置
- ✅ **docker-compose.yml** - Docker Compose 配置
- ✅ **.env.example** - 环境变量模板（重命名 .env 为 .env.example）
- ✅ **.gitignore** - Git 忽略规则

### 📄 其他必需文件

- ✅ **LICENSE** - 开源协议（如果有）
- ✅ **data/sample_transaction.json** - 示例数据
- ✅ **data/sample_transactions.json** - 示例数据

---

## ❌ 不应上传到 GitHub 的文件

### 🔒 敏感信息

- ❌ **.env** - 包含真实 API Key 和密钥
- ❌ **任何包含真实 API Key 的文件**
- ❌ **任何包含密码的文件**
- ❌ **任何包含个人信息的文件**

### 🗄️ 数据库文件

- ❌ **payguard_crew.db** - SQLite 数据库
- ❌ ***.db** - 所有数据库文件
- ❌ **tests/test_data/*.db** - 测试数据库

### 📁 生成文件

- ❌ **__pycache__/** - Python 缓存
- ❌ ***.pyc** - 编译的 Python 文件
- ❌ **.pytest_cache/** - Pytest 缓存
- ❌ **.chroma/** - ChromaDB 向量数据库
- ❌ **logs/** - 日志文件
- ❌ **logs/*.log** - 所有日志

### 🎯 IDE 和编辑器文件

- ❌ **.vscode/** - VS Code 配置（可选保留 .vscode/settings.json 示例）
- ❌ **.idea/** - PyCharm 配置
- ❌ ***.swp** - Vim 临时文件
- ❌ **.DS_Store** - macOS 文件

### 📦 依赖和环境

- ❌ **venv/** - 虚拟环境
- ❌ **env/** - 虚拟环境
- ❌ **.venv/** - 虚拟环境
- ❌ **node_modules/** - Node.js 依赖（如果有）

### 🔧 临时文件

- ❌ ***.backup** - 备份文件
- ❌ ***.tmp** - 临时文件
- ❌ **README.md.backup** - 备份的 README

---

## 📋 .gitignore 配置检查

确保 `.gitignore` 文件包含以下内容：

```gitignore
# 环境变量和密钥
.env
*.key
*.pem
secrets/

# 数据库文件
*.db
*.sqlite
*.sqlite3

# Python 缓存
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 测试和覆盖率
.pytest_cache/
.coverage
htmlcov/
.tox/

# 虚拟环境
venv/
env/
ENV/
.venv/

# IDE 配置
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# 日志文件
logs/
*.log

# 向量数据库
.chroma/
chroma_db/

# 临时文件
*.tmp
*.backup
*.bak

# 构建输出
build/
dist/
*.egg-info/
```

---

## 🚀 发布前检查清单

### 1. 敏感信息检查 ✅

```bash
# 检查是否有 .env 文件
ls -la | grep "\.env$"

# 检查是否有 API Key
grep -r "sk-" . --include="*.py" --include="*.md" --include="*.txt"
grep -r "api_key" . --include="*.py" --include="*.md" --include="*.txt"

# 检查是否有密码
grep -r "password" . --include="*.py" --include="*.md" --include="*.txt"
```

### 2. 数据库文件检查 ✅

```bash
# 确认数据库文件不会被上传
find . -name "*.db" -type f
```

### 3. 日志文件检查 ✅

```bash
# 确认日志文件不会被上传
find . -name "*.log" -type f
```

### 4. 缓存文件检查 ✅

```bash
# 确认缓存不会被上传
find . -name "__pycache__" -type d
find . -name "*.pyc" -type f
```

### 5. 环境变量模板 ✅

```bash
# 确保有 .env.example 文件
ls -la .env.example
```

---

## 📝 发布步骤

### 步骤 1: 清理不需要的文件

```bash
# 删除数据库文件
rm -f *.db
rm -f tests/test_data/*.db

# 删除日志文件
rm -rf logs/*.log

# 删除缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
rm -rf .chroma/

# 删除备份文件
rm -f *.backup
```

### 步骤 2: 创建 .env.example

```bash
# 如果没有 .env.example，从 .env 创建模板
cp .env .env.example

# 编辑 .env.example，移除所有真实的 API Key
# 将真实的 key 替换为占位符
```

**.env.example 内容示例：**
```env
# 应用配置
APP_NAME=payguard-crew
APP_ENV=dev

# LLM 配置（可选）
LLM_PROVIDER=disabled              # 选项: openai, deepseek, ollama, disabled
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=

OLLAMA_MODEL=qwen2.5
OLLAMA_BASE_URL=http://localhost:11434/v1

# CrewAI 配置
ENABLE_CREWAI=false                # 是否启用 CrewAI 编排

# RAG 配置
RAG_TOP_K=3                        # 检索返回数量
PAYGUARD_DOCS_DIR=docs             # 知识库目录

# 数据库配置
SQLITE_DB_PATH=./payguard_crew.db  # SQLite 数据库路径

# LLM 超时配置
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2

# API 配置
CORS_ORIGINS=http://localhost:3000
ENABLE_METRICS=true
```

### 步骤 3: 初始化 Git 仓库

```bash
# 初始化仓库
git init

# 添加所有文件
git add .

# 检查将要提交的文件
git status

# 确认没有敏感文件
git status | grep -E "\.env$|\.db$|\.log$"

# 提交
git commit -m "Initial commit - PayGuard Crew v0.1.0"
```

### 步骤 4: 推送到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/payguard-crew.git

# 推送到 GitHub
git push -u origin main
```

---

## 📋 GitHub 仓库设置建议

### 1. 仓库信息

- **名称**: `payguard-crew` 或 `payguard-crew-starter`
- **描述**: AI Multi-Agent 支付风控与合规审计演示系统
- **主题标签**: 
  - `ai-agent`
  - `multi-agent`
  - `fastapi`
  - `crewai`
  - `payment-risk`
  - `compliance`
  - `rag`
  - `chromadb`
  - `fintech`

### 2. README.md 徽章

在 README.md 顶部添加：

```markdown
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.80+-orange.svg)](https://www.crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

### 3. LICENSE 文件

建议使用 **MIT License**：

```
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 4. GitHub Actions（可选）

创建 `.github/workflows/tests.yml`：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest tests/ -v
```

---

## ⚠️ 安全注意事项

### 1. 绝对不要提交的内容

- ❌ 真实的 API Key
- ❌ 数据库连接字符串（如果包含密码）
- ❌ 私钥文件（.key, .pem）
- ❌ 真实用户数据
- ❌ 生产环境配置

### 2. 如果不小心提交了敏感信息

```bash
# 从历史记录中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all

# 立即更换泄露的 API Key！
```

### 3. 使用 GitHub Secrets

如果需要 CI/CD，将敏感信息存储在 GitHub Secrets 中，而不是代码中。

---

## 📊 文件分类汇总

| 类别 | 可上传 | 不可上传 | 说明 |
|------|--------|----------|------|
| 文档 | ✅ 11个 | ❌ 0个 | 所有文档都可以上传 |
| 代码 | ✅ 全部 | ❌ 0个 | 所有代码都可以上传 |
| 配置 | ✅ 示例 | ❌ 真实配置 | 使用 .env.example |
| 数据库 | ❌ | ❌ 全部 | 不上传任何 .db 文件 |
| 日志 | ❌ | ❌ 全部 | 不上传任何 .log 文件 |
| 缓存 | ❌ | ❌ 全部 | 不上传 __pycache__ 等 |

---

## ✅ 最终检查清单

在推送到 GitHub 之前：

- [ ] 已删除所有 .db 文件
- [ ] 已删除所有 .log 文件
- [ ] 已删除所有 __pycache__ 目录
- [ ] 已删除 .chroma/ 目录
- [ ] 已删除 .env 文件
- [ ] 已创建 .env.example 文件
- [ ] .env.example 中没有真实的 API Key
- [ ] .gitignore 配置正确
- [ ] README.md 中没有敏感信息
- [ ] 所有代码注释中没有敏感信息
- [ ] 已添加 LICENSE 文件
- [ ] 已测试所有功能正常

---

## 🎉 发布后

### 1. 添加 GitHub Topics

在仓库设置中添加相关主题：
- ai-agent
- multi-agent
- fastapi
- crewai
- payment-risk
- compliance
- rag
- chromadb

### 2. 更新个人资料

在 GitHub 个人资料中 Pin 这个项目，方便展示。

### 3. 分享链接

- 在简历中添加 GitHub 链接
- 在社交媒体分享
- 在技术社区分享

---

**准备就绪！可以安全地发布到 GitHub 了！** 🚀
