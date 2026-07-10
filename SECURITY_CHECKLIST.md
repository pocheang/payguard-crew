# 🔒 GitHub 推送安全检查清单

> **最后更新**: 2026-07-10  
> **项目**: PayGuard v0.2.0

---

## ⚡ 快速检查

推送代码到GitHub前，运行这些命令：

```bash
# 1. 检查敏感文件状态
git status | grep -E "\.env|\.db|\.log"

# 2. 搜索暂存区中的密钥
git diff --cached | grep -iE "api_key|secret|password|token|sk-"

# 3. 查看将要提交的文件列表
git diff --cached --name-only

# 4. 验证 .gitignore 是否生效
git check-ignore .env .env.development .env.production *.db .chroma/
```

如果以上命令发现任何问题，**立即停止推送**！

---

## ✅ 可以安全推送的文件

### 1. 源代码
```
✅ app/**/*.py              # 后端Python代码
✅ frontend/src/**/*.vue    # Vue组件
✅ frontend/src/**/*.js     # JavaScript代码
✅ frontend/src/**/*.css    # 样式文件
✅ tests/**/*.py            # 测试代码
✅ scripts/**/*.py          # 工具脚本
```

### 2. 配置文件（仅模板）
```
✅ .env.example             # ✓ 环境变量模板（无真实密钥）
✅ .env.production.template # ✓ 生产环境模板
✅ .gitignore               # Git忽略规则
✅ .dockerignore            # Docker忽略规则
✅ requirements.txt         # Python依赖
✅ package.json             # Node.js依赖
✅ docker-compose.yml       # Docker编排
✅ Dockerfile               # Docker镜像定义
```

### 3. 文档
```
✅ README.md                # 项目说明
✅ docs/**/*.md             # 所有文档
✅ LICENSE                  # 开源协议
✅ CHANGELOG.md             # 变更日志
✅ CONTRIBUTING.md          # 贡献指南
```

### 4. 配置和脚本
```
✅ *.sh                     # Shell脚本
✅ *.ps1                    # PowerShell脚本
✅ Makefile                 # Make配置
✅ pytest.ini               # 测试配置
```

---

## ❌ 绝对不能推送的文件

### 🔴 高危险 - 包含真实密钥

#### 当前项目中存在的敏感文件：
```bash
❌ .env                     # 包含真实API密钥
❌ .env.development         # 开发环境密钥
❌ .env.production          # 生产环境密钥
❌ payguard_crew.db         # 用户数据和交易记录
❌ .chroma/                 # 向量数据库
```

**状态**: ✅ 已被 `.gitignore` 保护

#### 这些文件包含：
- OpenAI API Key (`sk-...`)
- DeepSeek API Key
- JWT密钥 (`your-super-secret-jwt-key-...`)
- 数据库密码
- Redis密码
- 用户数据
- 交易记录

### 🟡 中危险 - 可能泄露隐私

```
❌ logs/**/*.log            # 应用日志（可能含敏感信息）
❌ *.db / *.sqlite          # 所有数据库文件
❌ __pycache__/             # Python缓存
❌ node_modules/            # Node依赖（体积巨大）
❌ dist/ / build/           # 构建产物
❌ .coverage               # 测试覆盖率
```

---

## 🛡️ 推送前必须执行的检查

### 检查1: 验证敏感文件被忽略
```bash
git check-ignore .env .env.development .env.production *.db .chroma/
```
✅ **期望输出**: 每个文件都应该显示被忽略

### 检查2: 搜索真实API密钥
```bash
# 检查暂存区
git diff --cached | grep -iE "sk-[a-zA-Z0-9]{20,}|key.*[0-9a-f]{32,}"

# 检查所有提交的文件
git grep -iE "sk-[a-zA-Z0-9]{20,}" -- '*.env.*'
```
❌ **期望输出**: 无任何结果

### 检查3: 查看将提交的文件
```bash
git status
git diff --cached --name-only
```

### 检查4: 验证已跟踪的环境文件
```bash
# 确认只有模板文件被跟踪
git ls-files | grep "\.env"
```
✅ **期望输出**: 只有 `.env.example` 和 `.env.*.template`

---

## 🚨 如果不小心推送了敏感信息

### 立即行动清单：

#### 1. 立即轮换所有密钥（最优先）
- [ ] OpenAI API密钥 → https://platform.openai.com/api-keys
- [ ] DeepSeek API密钥
- [ ] JWT密钥（生成新的随机密钥）
- [ ] 数据库密码
- [ ] Redis密码

#### 2. 从Git历史中删除敏感文件
```bash
# 使用 BFG Repo-Cleaner (推荐)
bfg --delete-files .env
bfg --delete-files .env.production
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 或使用 git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env .env.development .env.production" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送清理后的历史
git push --force --all
```

⚠️ **警告**: 这会重写整个Git历史！

#### 3. 通知GitHub
如果密钥已公开：
- 访问仓库设置 → Security → Secrets
- 检查是否有可疑的API使用

---

## 📋 提交前自检清单

推送前，逐项确认：

- [ ] ✅ `.env` 文件不在 `git status` 中
- [ ] ✅ `.env.development` 不在 `git status` 中
- [ ] ✅ `.env.production` 不在 `git status` 中
- [ ] ✅ 没有 `.db` 文件要提交
- [ ] ✅ 没有 `.log` 文件要提交
- [ ] ✅ 运行了 `git diff --cached | grep -i "sk-"` 无结果
- [ ] ✅ `.gitignore` 包含所有敏感文件类型
- [ ] ✅ 提交的 `.env.example` 只包含占位符
- [ ] ✅ 代码中没有硬编码的密钥
- [ ] ✅ 文档中的示例使用占位符
- [ ] ✅ 测试数据不包含真实信息

---

## 📖 相关文档

- [完整GitHub指南](docs/guides/GITHUB_GUIDE.md) - 详细的提交规则
- [环境配置指南](docs/guides/ENVIRONMENT_GUIDE.md) - 环境变量说明
- [贡献指南](CONTRIBUTING.md) - 参与开发规范

---

## 🔍 定期审计

**每月执行一次**：

```bash
# 1. 检查是否有敏感文件被误提交
git log --all --full-history -- "*.env" "*.db" "*.log"

# 2. 搜索历史中的密钥
git log -p -S "sk-" -- "*.py" "*.js" "*.md"

# 3. 审查最近的提交
git log --oneline -20
```

---

## 📞 安全问题联系

如果发现安全问题，请联系：
- 📧 Email: po.cheang@gmail.com
- 🔒 私密报告: https://github.com/pocheang/payguard-crew/security/advisories/new

---

**记住**: 一旦推送到GitHub，就应该假定密钥已泄露。预防胜于补救！
