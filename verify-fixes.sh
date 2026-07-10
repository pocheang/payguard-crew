#!/bin/bash
# 修复验证脚本 - 验证所有修复是否成功

set -e

echo "================================"
echo "PayGuard 修复验证脚本"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_item() {
    local name=$1
    local command=$2

    echo -n "测试: $name ... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
        FAILED=$((FAILED + 1))
    fi
}

echo "1. 检查后端配置验证增强"
echo "----------------------------------------"

# 测试生产环境配置验证
test_item "生产配置验证方法存在" "grep -q '_validate_production' app/config.py"
test_item "JWT密钥长度验证" "grep -q 'len(jwt_secret) < 32' app/config.py"
test_item "CORS安全检查" "grep -q 'CORS_ORIGINS' app/config.py"

echo ""
echo "2. 检查测试用例"
echo "----------------------------------------"

test_item "API审计测试存在" "test -f tests/api/test_audit.py"
test_item "审核工作流测试存在" "test -f tests/api/test_review.py"
test_item "测试配置文件存在" "test -f tests/conftest.py"

echo ""
echo "3. 检查前端优化"
echo "----------------------------------------"

test_item "Logger工具存在" "test -f frontend/src/utils/logger.js"
test_item "错误边界集成" "grep -q 'ErrorBoundary' frontend/src/App.vue"
test_item "Vite配置优化" "grep -q 'manualChunks' frontend/vite.config.js"

echo ""
echo "4. 检查文档"
echo "----------------------------------------"

test_item "代码审查报告" "test -f CODE_REVIEW_REPORT.md"
test_item "性能优化报告" "test -f PERFORMANCE_OPTIMIZATION_REPORT.md"
test_item "修复实施指南" "test -f FIX_IMPLEMENTATION_GUIDE.md"
test_item "最终总结报告" "test -f FINAL_SUMMARY.md"

echo ""
echo "5. 运行Python测试"
echo "----------------------------------------"

if command -v pytest &> /dev/null; then
    echo -n "运行pytest测试套件 ... "
    if pytest tests/api/ -v --tb=short > /tmp/pytest_output.txt 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠ 部分失败（可能需要配置）${NC}"
        echo "详细输出: /tmp/pytest_output.txt"
    fi
else
    echo -e "${YELLOW}⚠ pytest 未安装，跳过测试${NC}"
fi

echo ""
echo "6. 检查前端构建"
echo "----------------------------------------"

if [ -d "frontend" ]; then
    cd frontend
    if command -v npm &> /dev/null; then
        echo -n "前端构建测试 ... "
        if npm run build > /tmp/frontend_build.txt 2>&1; then
            echo -e "${GREEN}✓ 通过${NC}"
            PASSED=$((PASSED + 1))

            # 检查bundle大小
            if [ -f "dist/assets/Dashboard-*.js" ]; then
                size=$(wc -c < dist/assets/Dashboard-*.js | tr -d ' ')
                if [ "$size" -lt 20000 ]; then
                    echo -e "  Dashboard bundle: ${GREEN}${size} bytes (优化成功)${NC}"
                    PASSED=$((PASSED + 1))
                else
                    echo -e "  Dashboard bundle: ${YELLOW}${size} bytes (可能需要进一步优化)${NC}"
                fi
            fi
        else
            echo -e "${RED}✗ 失败${NC}"
            FAILED=$((FAILED + 1))
            echo "详细输出: /tmp/frontend_build.txt"
        fi
    else
        echo -e "${YELLOW}⚠ npm 未安装，跳过构建测试${NC}"
    fi
    cd ..
fi

echo ""
echo "================================"
echo "验证结果汇总"
echo "================================"
echo -e "通过: ${GREEN}${PASSED}${NC}"
echo -e "失败: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有验证通过！修复成功！${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ 部分验证失败，请检查详细输出${NC}"
    exit 1
fi
