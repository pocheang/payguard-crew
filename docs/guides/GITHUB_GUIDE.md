# PayGuard GitHub 提交指南

## 📋 文件分类清单

### ✅ 可以提交（安全）

#### 1. 源代码文件
```
✅ app/**/*.py              # Python 源码
✅ frontend/src/**/*.vue    # Vue 组件
✅ frontend/src/**/*.js     # JavaScript 文件
✅ frontend/src/**/*.css    # 样式文件
✅ scripts/**/*.py          # 工具脚本
✅ tests/**/*.py            # 测试文件
```

#### 2. 配置文件（无敏感信息）
```
✅ .gitignore               # Git 忽略规则
✅ .dockerignore            # Docker 忽略规则
✅ .env.example             # 环境变量模板（示例）
✅ requirements.txt         # Python 依赖
✅ package.json             # Node.js 依赖
✅ package-lock.json        # 锁定版本
✅ pyproject.toml           # Python 项目配置
✅ pytest.ini               # 测试配置
✅ tailwind.config.js       # Tailwind 配置
✅ vite.config.js           # Vite 配置
✅ postcss.config.js        # PostCSS 配置
```

#### 3. Docker 文件
```
✅ Dockerfile               # 后端 Docker 镜像
✅ frontend/Dockerfile      # 前端 Docker 镜像
✅ docker-compose.yml       # Docker 编排（简单模式）
✅ docker-compose.dev.yml   # 开发模式
✅ docker-compose.full.yml  # 完整模式
✅ docker-compose.prod.yml  # 生产模式
✅ nginx.conf               # Nginx 配置
```

#### 4. 文档文件
```
✅ README.md                # 项目说明
✅ *.md                     # 所有 Markdown 文档
✅ docs/**/*                # 文档目录
✅ LICENSE                  # 开源协议
✅ CHANGELOG.md             # 变更日志
✅ CONTRIBUTING.md          # 贡献指南
```

#### 5. 脚本文件
```
✅ *.sh                     # Bash 脚本
✅ *.ps1                    # PowerShell 脚本
✅ deploy.sh                # 部署脚本
✅ deploy.ps1               # Windows 部署脚本
✅ fix-issues.sh            # 修复脚本
✅ check-system.sh          # 检查脚本
```

#### 6. 前端资源
```
✅ frontend/public/**/*     # 公共资源
✅ frontend/index.html      # HTML 入口
✅ frontend/src/assets/**/* # 前端资源
```

---

### ❌ 绝对不能提交（敏感信息）

#### 1. 环境变量文件（包含真实密钥）
```
❌ .env                     # 真实环境变量
❌ .env.local               # 本地环境变量
❌ .env.production          # 生产环境变量
❌ .env.development         # 开发环境变量（如有真实密钥）
❌ *.env.backup             # 环境变量备份
```

**为什么不能提交**：
- 包含 API 密钥（OpenAI, DeepSeek）
- 包含 JWT 密钥
- 包含数据库密码
- 包含 Redis 密码

#### 2. 数据库文件
```
❌ *.db                     # SQLite 数据库
❌ *.sqlite                 # SQLite 数据库
❌ *.sqlite3                # SQLite 数据库
❌ payguard_crew.db         # 项目数据库
❌ data/**/*.db             # 数据目录
```

**为什么不能提交**：
- 包含用户数据
- 包含交易记录
- 文件体积大

#### 3. 日志文件
```
❌ logs/**/*                # 所有日志
❌ *.log                    # 日志文件
❌ app.log                  # 应用日志
❌ error.log                # 错误日志
```

**为什么不能提交**：
- 可能包含敏感信息
- 文件体积大
- 频繁变化

#### 4. 缓存和临时文件
```
❌ __pycache__/             # Python 缓存
❌ *.pyc                    # Python 字节码
❌ *.pyo                    # Python 优化字节码
❌ .pytest_cache/           # Pytest 缓存
❌ .coverage                # 测试覆盖率
❌ htmlcov/                 # 覆盖率报告
❌ .mypy_cache/             # MyPy 缓存
```

#### 5. Node.js 文件
```
❌ node_modules/            # Node.js 依赖（巨大）
❌ .npm/                    # NPM 缓存
❌ npm-debug.log            # NPM 调试日志
❌ yarn-error.log           # Yarn 错误日志
```

#### 6. IDE 和编辑器配置（个人化）
```
❌ .vscode/settings.json    # VS Code 个人设置
❌ .idea/                   # PyCharm 配置
❌ *.swp                    # Vim 交换文件
❌ *.swo                    # Vim 临时文件
❌ .DS_Store                # macOS 系统文件
❌ Thumbs.db                # Windows 系统文件
```

#### 7. 构建产物
```
❌ dist/                    # 前端构建输出
❌ build/                   # 构建目录
❌ *.whl                    # Python 包
❌ *.egg-info/              # Python 包信息
```

#### 8. 向量数据库
```
❌ .chroma/                 # ChromaDB 数据
❌ chroma_db/               # 向量数据库
❌ *.index                  # 索引文件
```

#### 9. 备份文件
```
❌ *.bak                    # 备份文件
❌ *.backup                 # 备份文件
❌ *.old                    # 旧文件
❌ *~                       # 临时备份
```

---

### ⚠️ 特殊处理（需要审查）

#### 1. 配置文件（可能包含敏感信息）
```
⚠️ config.yaml              # 检查是否有密钥
⚠️ config.json              # 检查是否有密钥
⚠️ settings.py              # 检查是否有硬编码密钥
```

**处理方式**：
- 使用环境变量替代硬编码
- 只提交模板文件（如 config.example.yaml）

#### 2. 测试数据
```
⚠️ tests/fixtures/*.json    # 检查是否有真实数据
⚠️ tests/data/*.csv         # 检查是否有敏感信息
```

**处理方式**：
- 只使用虚拟数据
- 移除真实用户信息

#### 3. 文档中的示例
```
⚠️ docs/**/*.md             # 检查示例代码中的密钥
⚠️ README.md                # 检查是否有真实凭据
```

**处理方式**：
- 使用占位符（如 `your-api-key-here`）
- 不要粘贴真实的 API 密钥

---

## 📝 完整的 .gitignore 配置

```gitignore
# ============================================
# PayGuard .gitignore
# ============================================

# ==================== Python ====================
# 字节码文件
__pycache__/
*.py[cod]
*$py.class

# 分发/打包
dist/
build/
*.egg-info/
*.egg

# 虚拟环境
venv/
env/
ENV/
.venv

# 测试和覆盖率
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/

# ==================== Node.js ====================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json.bak

# ==================== 环境变量 ====================
# 真实环境变量（绝对不提交）
.env
.env.local
.env.*.local
.env.development
.env.production

# 只保留示例文件
!.env.example

# ==================== 数据库 ====================
*.db
*.sqlite
*.sqlite3
payguard_crew.db

# 数据目录
data/
!data/.gitkeep

# ==================== 日志 ====================
logs/
*.log
app.log
error.log
!logs/.gitkeep

# ==================== 向量数据库 ====================
.chroma/
chroma_db/
*.index

# ==================== IDE 配置 ====================
# VS Code
.vscode/
!.vscode/extensions.json
!.vscode/settings.json.example

# PyCharm
.idea/

# ==================== 操作系统 ====================
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Linux
*~
.directory

# ==================== 构建产物 ====================
dist/
build/
*.whl

# 前端构建
frontend/dist/
frontend/build/

# ==================== 临时文件 ====================
*.swp
*.swo
*.tmp
*.temp
*.bak
*.backup
*.old

# ==================== Docker ====================
# 不忽略 Docker 文件，但忽略数据卷
!Dockerfile
!docker-compose*.yml
# Docker 数据卷内容
.docker-data/

# ==================== 其他 ====================
# 测试覆盖率
.coverage.*
coverage.xml
*.cover

# Jupyter Notebook
.ipynb_checkpoints

# 证书和密钥
*.pem
*.key
*.crt
*.p12
```

---

## 🛡️ 安全检查清单

### 提交前必须检查：

- [ ] `.env` 文件不在提交列表中
- [ ] 没有真实的 API 密钥
- [ ] 没有数据库密码
- [ ] 没有 JWT 密钥
- [ ] 没有真实用户数据
- [ ] 没有生产环境配置
- [ ] README 中的示例使用占位符
- [ ] 代码注释中没有密码
- [ ] 没有硬编码的凭据

### 检查命令：

```bash
# 检查是否有 .env 文件要提交
git status | grep ".env"

# 搜索可能的密钥（在提交前运行）
git diff --cached | grep -i "api_key\|secret\|password\|token"

# 检查已暂存的文件
git diff --cached --name-only

# 查看将要提交的内容
git diff --cached
```

---

## 🔒 密钥管理最佳实践

### 1. 使用环境变量
```python
# ❌ 错误：硬编码
API_KEY = "sk-abc123xyz789"

# ✅ 正确：环境变量
API_KEY = os.getenv("OPENAI_API_KEY")
```

### 2. 提供示例文件
```bash
# 提供 .env.example
cp .env .env.example

# 移除所有真实值
sed -i 's/sk-[a-zA-Z0-9]*/your-api-key-here/g' .env.example
```

### 3. 文档中使用占位符
```markdown
# ❌ 错误
OPENAI_API_KEY=sk-abc123real-key

# ✅ 正确
OPENAI_API_KEY=your-openai-api-key-here
```

---

## 📦 准备提交到 GitHub

### 步骤1：清理敏感文件
```bash
# 删除可能存在的敏感文件
rm -f .env .env.local *.db logs/*.log

# 清理缓存
rm -rf __pycache__ node_modules .pytest_cache
```

### 步骤2：验证 .gitignore
```bash
# 查看将被提交的文件
git status

# 如果有不应该提交的文件，添加到 .gitignore
echo "sensitive-file.txt" >> .gitignore
```

### 步骤3：首次提交
```bash
# 添加所有文件
git add .

# 查看即将提交的文件
git status

# 检查是否有敏感信息
git diff --cached | grep -i "api_key\|secret\|password"

# 提交
git commit -m "Initial commit: PayGuard payment risk control system"

# 推送到 GitHub
git remote add origin https://github.com/yourusername/payguard.git
git push -u origin main
```

---

## ⚡ 快速检查脚本

我会创建一个检查脚本来自动扫描敏感信息...
