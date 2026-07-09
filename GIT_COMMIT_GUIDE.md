# PayGuard Git 提交指南

## 📋 提交前准备清单

在提交代码到Git之前，请完成以下步骤：

### ✅ 必须完成

- [ ] 删除所有敏感文件
  ```bash
  # 删除环境变量文件（保留 .env.example）
  rm -f .env .env.local .env.production
  
  # 删除数据库文件
  rm -f *.db app/data/*.db frontend/data/*.db
  rm -rf tests/test_data/*.db
  
  # 删除日志文件
  rm -rf logs/*.log
  ```

- [ ] 运行安全检查脚本
  ```bash
  # Linux/Mac
  ./check-before-commit.sh
  
  # Windows
  .\check-before-commit.ps1
  ```

- [ ] 验证 .gitignore
  ```bash
  git status
  # 确保没有敏感文件在列表中
  ```

- [ ] 检查暂存的文件
  ```bash
  git diff --cached --name-only
  ```

- [ ] 搜索敏感关键词
  ```bash
  git diff --cached | grep -iE "api_key|secret|password|token|sk-"
  ```

### ⚠️ 可选但推荐

- [ ] 运行测试
  ```bash
  pytest
  ```

- [ ] 检查代码风格
  ```bash
  black app/
  isort app/
  ```

- [ ] 验证前端构建
  ```bash
  cd frontend
  npm run build
  ```

---

## 🚀 初始化Git仓库

如果这是首次提交：

```bash
# 1. 初始化仓库（如果还没有）
git init

# 2. 添加远程仓库
git remote add origin https://github.com/yourusername/payguard.git

# 3. 设置默认分支
git branch -M main
```

---

## 📝 版本 0.2.0 提交步骤

### 步骤1：清理敏感文件

```bash
# 一键清理脚本
cat > clean-sensitive.sh << 'EOF'
#!/bin/bash
echo "🧹 清理敏感文件..."

# 删除环境变量
rm -f .env .env.local .env.production .env.production.template
echo "✓ 已删除环境变量文件"

# 删除数据库
rm -f *.db app/data/*.db frontend/data/*.db
rm -rf tests/test_data/*.db
echo "✓ 已删除数据库文件"

# 删除日志
rm -rf logs/*.log
echo "✓ 已删除日志文件"

# 删除缓存
rm -rf __pycache__ .pytest_cache .mypy_cache
rm -rf frontend/node_modules frontend/dist
echo "✓ 已删除缓存文件"

echo "✅ 清理完成！"
EOF

chmod +x clean-sensitive.sh
./clean-sensitive.sh
```

### 步骤2：验证文件列表

```bash
# 查看将要提交的文件
git status

# 应该看到的文件类型：
# ✅ .py, .vue, .js, .css 源代码
# ✅ .md 文档
# ✅ .sh, .ps1 脚本
# ✅ Dockerfile, docker-compose*.yml
# ✅ .env.example (示例文件)
# ✅ .gitignore

# 不应该看到：
# ❌ .env (真实环境变量)
# ❌ *.db (数据库)
# ❌ *.log (日志)
# ❌ node_modules/
# ❌ __pycache__/
```

### 步骤3：添加文件

```bash
# 添加所有文件
git add .

# 或选择性添加
git add app/ frontend/src/ *.md *.sh *.ps1 Dockerfile docker-compose*.yml .gitignore
```

### 步骤4：运行安全检查

```bash
# Linux/Mac
./check-before-commit.sh

# Windows
.\check-before-commit.ps1

# 如果检查失败，根据提示修复问题
```

### 步骤5：创建提交

```bash
# 提交代码
git commit -m "Release v0.2.0: Complete system with Docker one-click deployment

Major Features:
- ✨ Complete frontend with 9 components and 7 pages
- 🐳 Docker one-click deployment (3 modes)
- 📖 Comprehensive documentation (8 guides)
- 🔒 Security enhancements and pre-commit checks
- ⚡ Performance optimizations (30-60% smaller images)

New Components:
- ErrorBoundary, Loading, Pagination

New Features:
- Environment variable configuration
- Dynamic API URL
- Production-ready Docker configs
- Security check scripts

Documentation:
- Complete README.md
- STARTUP_GUIDE.md
- DOCKER_DEPLOYMENT.md
- LLM_CONFIG_GUIDE.md
- GITHUB_GUIDE.md
- ONE_CLICK_DEPLOY.md

See CHANGELOG.md for full details."
```

### 步骤6：创建标签

```bash
# 创建版本标签
git tag -a v0.2.0 -m "Version 0.2.0 - Complete system with Docker deployment"

# 查看标签
git tag -l
```

### 步骤7：推送到GitHub

```bash
# 推送代码
git push -u origin main

# 推送标签
git push origin v0.2.0

# 或一起推送
git push origin main --tags
```

---

## 📊 提交后验证

### 验证GitHub上的文件

访问你的GitHub仓库，确认：

- ✅ README.md 正确显示
- ✅ 没有 .env 文件
- ✅ 没有 .db 文件
- ✅ 没有 node_modules/
- ✅ 文档完整可访问
- ✅ 标签 v0.2.0 存在

### 创建GitHub Release

1. 访问 GitHub 仓库
2. 点击 "Releases"
3. 点击 "Create a new release"
4. 选择标签 `v0.2.0`
5. 填写 Release 信息：

```markdown
# PayGuard v0.2.0 - Complete System Release 🎉

## 🌟 Highlights

- **One-Click Deployment**: Deploy in 2-5 minutes with interactive scripts
- **Complete Frontend**: 9 components, 7 pages, modern UI
- **Docker Ready**: 4 deployment modes for different scenarios
- **Comprehensive Docs**: 8 detailed guides covering everything
- **Security Enhanced**: Pre-commit checks, non-root containers
- **Optimized Images**: 30-60% smaller Docker images

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/payguard.git
cd payguard

# Run one-click deployment
./deploy.sh  # Linux/Mac
.\deploy.ps1 # Windows
```

## 📖 Documentation

- [README](README.md) - Project overview
- [Startup Guide](STARTUP_GUIDE.md) - Get started in 3 ways
- [Docker Deployment](DOCKER_DEPLOYMENT.md) - Complete Docker guide
- [LLM Configuration](LLM_CONFIG_GUIDE.md) - AI model setup
- [GitHub Guide](GITHUB_GUIDE.md) - Contribution guide

## 📦 What's New in 0.2.0

### Frontend
- 3 new components (ErrorBoundary, Loading, Pagination)
- Environment variable configuration
- Dynamic API URL support
- Improved error handling

### Docker & Deployment
- One-click deployment scripts
- 4 deployment modes (simple, dev, full, production)
- Optimized Dockerfiles (30-60% smaller)
- Production-ready configurations

### Documentation
- Complete README with badges
- 8 comprehensive guides
- Security best practices
- Contribution guidelines

### Developer Tools
- Security check scripts
- System health check
- Automated fix scripts
- Complete .gitignore

## 🔄 Upgrade from 0.1.x

```bash
git pull origin main
./deploy.sh
```

## 🙏 Contributors

Thank you to all contributors who made this release possible!

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
```

6. 点击 "Publish release"

---

## 🔄 后续版本提交

### 功能开发分支

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 开发和提交
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/your-feature-name

# 在GitHub创建Pull Request
```

### 版本升级

```bash
# 更新版本号
echo "0.3.0" > VERSION

# 更新CHANGELOG.md
# ... 添加新版本内容

# 提交
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 0.3.0"

# 创建标签
git tag -a v0.3.0 -m "Version 0.3.0"

# 推送
git push origin main --tags
```

---

## 💡 提交消息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

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
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链

### 示例

```bash
feat(frontend): add pagination component

- Add Pagination.vue component
- Support smart page number display
- Add responsive design
- Update documentation

Closes #123
```

---

## 🆘 常见问题

### Q1: 不小心提交了敏感文件怎么办？

```bash
# 从Git历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（注意：这会改写历史）
git push origin --force --all
git push origin --force --tags
```

### Q2: 如何撤销最后一次提交？

```bash
# 保留更改
git reset --soft HEAD~1

# 丢弃更改
git reset --hard HEAD~1
```

### Q3: 如何修改最后一次提交消息？

```bash
git commit --amend -m "新的提交消息"
git push origin main --force
```

---

## 📞 需要帮助？

- 📖 查看 [GITHUB_GUIDE.md](GITHUB_GUIDE.md)
- 🔒 运行 `./check-before-commit.sh`
- 📋 查看 [CHANGELOG.md](CHANGELOG.md)
- 💬 提交 [GitHub Issue](https://github.com/yourusername/payguard/issues)

---

**🎉 准备好了！现在可以提交 v0.2.0 到GitHub了！**
