#!/bin/bash

# 提交 v0.2.0 快速脚本

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          🚀 提交 PayGuard v0.2.0                          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 最后检查
echo "📋 执行最后安全检查..."
echo ""

# 检查敏感文件
SENSITIVE=$(git diff --cached --name-only | grep -E "^\.env$|\.db$|\.log$|node_modules|__pycache__" || true)
if [ -n "$SENSITIVE" ]; then
    echo "❌ 发现敏感文件！"
    echo "$SENSITIVE"
    exit 1
fi

echo "✓ 没有敏感文件"
echo "✓ 暂存区有 $(git diff --cached --name-only | wc -l) 个文件"
echo ""

# 显示提交信息
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 提交信息："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "标题: Release v0.2.0: Complete system with Docker deployment"
echo ""
echo "描述:"
echo "  - Frontend: 9 components, 7 pages"
echo "  - Docker: One-click deployment (4 modes)"
echo "  - Docs: 8 comprehensive guides"
echo "  - Security: Enhanced checks"
echo "  - Performance: 30-60% smaller images"
echo ""

# 确认
read -p "确认提交？(y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消提交"
    exit 1
fi

echo ""
echo "📦 创建提交..."

# 创建提交
git commit -m "Release v0.2.0: Complete system with Docker deployment

Major Features:
✨ Frontend: 9 reusable components, 7 complete pages
🐳 Docker: One-click deployment (simple/dev/full/production modes)
📖 Documentation: 8 comprehensive guides
🔒 Security: Pre-commit checks, non-root containers
⚡ Performance: 30-60% smaller Docker images

New Components:
- ErrorBoundary: Error boundary with retry
- Loading: Loading indicator with modes
- Pagination: Smart pagination component

New Features:
- Environment variable configuration
- Dynamic API URL detection
- Production-ready Docker configs
- Security check scripts (check-before-commit.sh/ps1)

Backend Refactoring:
- Reorganized app/agents/runners structure
- Added batch audit API
- Added review workflow API
- Enhanced security and error handling

Docker Improvements:
- Multi-stage builds for smaller images
- 4 deployment modes (simple/dev/full/prod)
- Non-root user for security
- Optimized layer caching
- Resource limits and health checks

Documentation:
- Professional README.md with badges
- STARTUP_GUIDE.md - 3 ways to start
- DOCKER_DEPLOYMENT.md - Complete Docker guide
- LLM_CONFIG_GUIDE.md - Model configuration
- GITHUB_GUIDE.md - Submission guide
- ONE_CLICK_DEPLOY.md - One-click deployment
- CHANGELOG.md - Full change history
- GIT_COMMIT_GUIDE.md - Commit guide

Developer Tools:
- Security check scripts
- System health check script
- Comprehensive .gitignore
- Automated fix scripts

See CHANGELOG.md for full details."

if [ $? -eq 0 ]; then
    echo "✓ 提交成功"
    echo ""

    # 创建标签
    echo "🏷️  创建版本标签 v0.2.0..."
    git tag -a v0.2.0 -m "Version 0.2.0 - Complete system with Docker one-click deployment

Major highlights:
- One-click Docker deployment
- Complete frontend with 9 components
- 8 comprehensive documentation guides
- Enhanced security features
- Optimized Docker images (30-60% smaller)
- Production-ready configurations"

    if [ $? -eq 0 ]; then
        echo "✓ 标签创建成功"
        echo ""

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 完成！"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "下一步："
        echo "  1. 推送到远程: git push origin main"
        echo "  2. 推送标签:   git push origin v0.2.0"
        echo "  或一起推送:     git push origin main --tags"
        echo ""
    else
        echo "❌ 标签创建失败"
        exit 1
    fi
else
    echo "❌ 提交失败"
    exit 1
fi
