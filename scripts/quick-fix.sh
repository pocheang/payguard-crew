#!/bin/bash
# quick-fix.sh - 快速修复脚本

set -e  # 遇到错误立即退出

echo "🚀 PayGuard Crew 快速优化脚本"
echo "================================"

# 1. 检查 Python 版本
echo ""
echo "📋 1. 检查 Python 版本..."
python --version

# 2. 安装开发依赖
echo ""
echo "📦 2. 安装开发依赖..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    echo "✅ 开发依赖安装完成"
else
    echo "⚠️  requirements-dev.txt 不存在，跳过"
fi

# 3. 代码格式化
echo ""
echo "🎨 3. 代码格式化..."
if command -v black &> /dev/null; then
    black app/ tests/ --line-length 100
    echo "✅ Black 格式化完成"
else
    echo "⚠️  Black 未安装，跳过格式化"
fi

# 4. 代码检查
echo ""
echo "🔍 4. 代码语法检查..."
if command -v ruff &> /dev/null; then
    ruff check app/ tests/ --fix || echo "⚠️  发现一些问题，请手动修复"
    echo "✅ Ruff 检查完成"
else
    echo "⚠️  Ruff 未安装，跳过检查"
fi

# 5. 运行测试
echo ""
echo "🧪 5. 运行测试..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short || echo "⚠️  部分测试失败"
    echo "✅ 测试完成"
else
    echo "⚠️  Pytest 未安装，跳过测试"
fi

# 6. 测试覆盖率
echo ""
echo "📊 6. 生成测试覆盖率报告..."
if command -v pytest &> /dev/null; then
    pytest --cov=app --cov-report=term-missing --cov-report=html || echo "⚠️  覆盖率报告生成失败"
    echo "✅ 覆盖率报告已生成到 htmlcov/index.html"
else
    echo "⚠️  Pytest 未安装，跳过覆盖率"
fi

# 7. 依赖安全扫描
echo ""
echo "🔒 7. 依赖安全扫描..."
if command -v safety &> /dev/null; then
    safety check --json || echo "⚠️  发现安全问题"
    echo "✅ 安全扫描完成"
else
    echo "⚠️  Safety 未安装，跳过安全扫描"
fi

# 8. 类型检查
echo ""
echo "🔬 8. 类型检查..."
if command -v mypy &> /dev/null; then
    mypy app/ --ignore-missing-imports || echo "⚠️  发现类型问题"
    echo "✅ 类型检查完成"
else
    echo "⚠️  Mypy 未安装，跳过类型检查"
fi

echo ""
echo "================================"
echo "✅ 快速优化完成！"
echo ""
echo "📝 生成的文件："
echo "   - htmlcov/index.html (测试覆盖率报告)"
echo ""
echo "💡 下一步："
echo "   1. 查看测试覆盖率: open htmlcov/index.html"
echo "   2. 启动服务: uvicorn app.main:app --reload"
echo "   3. 查看 API 文档: http://127.0.0.1:8000/docs"
