#!/bin/bash
# GitHub 发布前检查脚本
# 用于检查是否有不应该上传的敏感文件

echo "=========================================="
echo "🔍 GitHub 发布前安全检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
ERRORS=0
WARNINGS=0

echo "1️⃣ 检查敏感文件..."
echo ""

# 检查 .env 文件
if [ -f ".env" ]; then
    echo -e "${RED}❌ 发现 .env 文件 - 不应上传！${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 未发现 .env 文件${NC}"
fi

# 检查 .env.example 是否存在
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✅ .env.example 存在${NC}"
else
    echo -e "${YELLOW}⚠️  .env.example 不存在 - 建议创建${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "2️⃣ 检查数据库文件..."
echo ""

# 检查数据库文件
DB_FILES=$(find . -name "*.db" -not -path "./.git/*" 2>/dev/null | wc -l)
if [ $DB_FILES -gt 0 ]; then
    echo -e "${RED}❌ 发现 $DB_FILES 个数据库文件：${NC}"
    find . -name "*.db" -not -path "./.git/*" 2>/dev/null
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 未发现数据库文件${NC}"
fi

echo ""
echo "3️⃣ 检查日志文件..."
echo ""

# 检查日志文件
LOG_FILES=$(find . -name "*.log" -not -path "./.git/*" 2>/dev/null | wc -l)
if [ $LOG_FILES -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $LOG_FILES 个日志文件：${NC}"
    find . -name "*.log" -not -path "./.git/*" 2>/dev/null
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ 未发现日志文件${NC}"
fi

echo ""
echo "4️⃣ 检查 API Key..."
echo ""

# 检查是否有未替换的 API Key（简单检查）
if grep -r "sk-[a-zA-Z0-9]" . --include="*.py" --include="*.md" --include="*.txt" --exclude-dir=".git" 2>/dev/null | grep -v ".env.example" > /dev/null; then
    echo -e "${RED}❌ 可能发现真实的 API Key！${NC}"
    grep -r "sk-[a-zA-Z0-9]" . --include="*.py" --include="*.md" --include="*.txt" --exclude-dir=".git" 2>/dev/null | grep -v ".env.example"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ 未发现明显的 API Key${NC}"
fi

echo ""
echo "5️⃣ 检查 ChromaDB 向量库..."
echo ""

if [ -d ".chroma" ]; then
    echo -e "${YELLOW}⚠️  发现 .chroma 目录${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ 未发现 .chroma 目录${NC}"
fi

echo ""
echo "6️⃣ 检查 __pycache__ 缓存..."
echo ""

CACHE_DIRS=$(find . -name "__pycache__" -not -path "./.git/*" 2>/dev/null | wc -l)
if [ $CACHE_DIRS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $CACHE_DIRS 个 __pycache__ 目录${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ 未发现 __pycache__ 目录${NC}"
fi

echo ""
echo "7️⃣ 检查 .gitignore..."
echo ""

if [ -f ".gitignore" ]; then
    echo -e "${GREEN}✅ .gitignore 存在${NC}"
else
    echo -e "${RED}❌ .gitignore 不存在！${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=========================================="
echo "📊 检查结果"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！可以安全发布到 GitHub${NC}"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $WARNINGS 个警告${NC}"
    echo -e "${YELLOW}建议清理后再发布${NC}"
    echo ""
    echo "运行以下命令清理："
    echo "  rm -rf .chroma/"
    echo "  find . -type d -name '__pycache__' -exec rm -rf {} +"
    echo "  rm -f logs/*.log"
    echo ""
    exit 1
else
    echo -e "${RED}❌ 发现 $ERRORS 个错误和 $WARNINGS 个警告${NC}"
    echo -e "${RED}请修复错误后再发布！${NC}"
    echo ""
    echo "修复建议："
    echo "  1. 删除 .env 文件（或将其添加到 .gitignore）"
    echo "  2. 删除所有 .db 文件"
    echo "  3. 检查并移除真实的 API Key"
    echo "  4. 创建 .env.example 模板文件"
    echo ""
    exit 1
fi
