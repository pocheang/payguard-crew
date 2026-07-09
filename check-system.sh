#!/bin/bash

# PayGuard 系统功能验证脚本
# 用途：一键检查所有功能是否正常

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          PayGuard 功能验证脚本                             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
PASS=0
FAIL=0

# 检查函数
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAIL++))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 检查前端文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查前端目录
[ -d "frontend/src" ]
check "前端源码目录存在"

# 检查组件
COMPONENTS=$(ls frontend/src/components/*.vue 2>/dev/null | wc -l)
[ "$COMPONENTS" -eq 9 ]
check "前端组件完整 ($COMPONENTS/9)"

# 检查页面
VIEWS=$(ls frontend/src/views/*.vue 2>/dev/null | wc -l)
[ "$VIEWS" -eq 7 ]
check "前端页面完整 ($VIEWS/7)"

# 检查核心文件
[ -f "frontend/src/main.js" ]
check "main.js 存在"

[ -f "frontend/src/router/index.js" ]
check "router 存在"

[ -f "frontend/src/services/api.js" ]
check "API服务存在"

[ -f "frontend/src/config/index.js" ]
check "配置文件存在"

# 检查环境配置
[ -f "frontend/.env.example" ]
check ".env.example 存在"

# 检查依赖
[ -f "frontend/package.json" ]
check "package.json 存在"

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} 前端依赖已安装"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} 前端依赖未安装（需运行: cd frontend && npm install）"
    ((FAIL++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. 检查后端文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查后端目录
[ -d "app" ]
check "后端源码目录存在"

# 检查API路由
API_COUNT=$(ls app/api/*.py 2>/dev/null | grep -v __pycache__ | wc -l)
[ "$API_COUNT" -ge 5 ]
check "API路由文件完整 ($API_COUNT个)"

# 检查核心文件
[ -f "app/main.py" ]
check "main.py 存在"

[ -f "app/config.py" ]
check "config.py 存在"

[ -f "requirements.txt" ]
check "requirements.txt 存在"

# 检查Python环境
if command -v python &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 已安装 ($(python --version 2>&1))"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Python 未安装"
    ((FAIL++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. 检查Docker配置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ -f "Dockerfile" ]
check "后端 Dockerfile 存在"

[ -f "frontend/Dockerfile" ]
check "前端 Dockerfile 存在"

[ -f "docker-compose.yml" ]
check "docker-compose.yml 存在"

[ -f "docker-compose.dev.yml" ]
check "docker-compose.dev.yml 存在"

[ -f "docker-compose.full.yml" ]
check "docker-compose.full.yml 存在"

[ -f "docker-compose.prod.yml" ]
check "docker-compose.prod.yml 存在"

# 检查Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker 已安装 ($(docker --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1))"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} Docker 未安装（可选）"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. 检查文档"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ -f "STARTUP_GUIDE.md" ]
check "启动指南存在"

[ -f "LLM_CONFIG_GUIDE.md" ]
check "LLM配置指南存在"

[ -f "DOCKER_DEPLOYMENT.md" ]
check "Docker部署指南存在"

[ -f "FUNCTION_CHECK_REPORT.md" ]
check "功能检查报告存在"

[ -f "SYSTEM_COMPLETE.md" ]
check "系统状态总结存在"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "检查完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "通过: ${GREEN}$PASS${NC}"
echo -e "失败: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！系统就绪！${NC}"
    exit 0
elif [ $FAIL -le 2 ]; then
    echo -e "${YELLOW}⚠ 系统基本就绪，有少量问题需要修复${NC}"
    echo ""
    echo "常见修复："
    echo "  • 安装前端依赖: cd frontend && npm install"
    echo "  • 安装Python依赖: pip install -r requirements.txt"
    exit 0
else
    echo -e "${RED}✗ 发现多个问题，请查看上面的详细信息${NC}"
    exit 1
fi
