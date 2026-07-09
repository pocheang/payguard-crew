#!/bin/bash

# PayGuard GitHub 提交安全检查脚本
# 用途：扫描可能包含敏感信息的文件

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          🔒 GitHub 提交安全检查                            ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

ISSUES_FOUND=0

# 检查 .env 文件
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 检查环境变量文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git status --short | grep -E "\.env$|\.env\.local|\.env\.production"; then
    echo -e "${RED}❌ 发现 .env 文件在暂存区！${NC}"
    echo "   以下文件不应提交："
    git status --short | grep -E "\.env$|\.env\.local|\.env\.production"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓${NC} 未发现 .env 文件"
fi

# 检查数据库文件
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. 检查数据库文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git status --short | grep -E "\.db$|\.sqlite"; then
    echo -e "${RED}❌ 发现数据库文件在暂存区！${NC}"
    git status --short | grep -E "\.db$|\.sqlite"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓${NC} 未发现数据库文件"
fi

# 检查日志文件
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. 检查日志文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git status --short | grep -E "\.log$|logs/"; then
    echo -e "${YELLOW}⚠${NC} 发现日志文件在暂存区"
    git status --short | grep -E "\.log$|logs/"
    echo "   建议：日志文件通常不应提交"
fi

# 扫描暂存文件中的敏感关键词
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. 扫描敏感关键词"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 关键词列表
KEYWORDS=(
    "api_key"
    "api-key"
    "apikey"
    "secret"
    "password"
    "passwd"
    "token"
    "auth_token"
    "private_key"
    "sk-[a-zA-Z0-9]{32,}"
)

FOUND_SENSITIVE=false

for keyword in "${KEYWORDS[@]}"; do
    if git diff --cached | grep -iE "$keyword" | grep -v "\.example" | grep -v "your-.*-here" | grep -v "GITHUB_GUIDE"; then
        if [ "$FOUND_SENSITIVE" = false ]; then
            echo -e "${RED}❌ 发现可能的敏感信息：${NC}"
            FOUND_SENSITIVE=true
            ((ISSUES_FOUND++))
        fi
    fi
done

if [ "$FOUND_SENSITIVE" = false ]; then
    echo -e "${GREEN}✓${NC} 未发现敏感关键词"
fi

# 检查大文件
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. 检查大文件 (>10MB)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LARGE_FILES=$(git diff --cached --name-only | xargs -I {} find {} -type f -size +10M 2>/dev/null)
if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠${NC} 发现大文件："
    echo "$LARGE_FILES"
    echo "   建议：使用 Git LFS 或不提交大文件"
else
    echo -e "${GREEN}✓${NC} 未发现大文件"
fi

# 检查 node_modules
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. 检查 node_modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git status --short | grep "node_modules"; then
    echo -e "${RED}❌ node_modules 在暂存区！${NC}"
    echo "   这会导致仓库体积巨大"
    ((ISSUES_FOUND++))
else
    echo -e "${GREEN}✓${NC} node_modules 未被追踪"
fi

# 总结
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "检查完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ 安全检查通过！可以提交到 GitHub${NC}"
    echo ""
    echo "建议的提交命令："
    echo "  git commit -m \"your commit message\""
    echo "  git push origin main"
    exit 0
else
    echo -e "${RED}✗ 发现 $ISSUES_FOUND 个问题，请修复后再提交${NC}"
    echo ""
    echo "修复建议："
    echo "  1. 移除敏感文件：git reset HEAD <file>"
    echo "  2. 添加到 .gitignore"
    echo "  3. 使用环境变量替代硬编码密钥"
    echo ""
    exit 1
fi
