#!/bin/bash
# PayGuard 问题修复脚本

set -e

echo "🔧 PayGuard 问题修复脚本"
echo "========================================"
echo ""

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo ""

# 1. 修复前端依赖
echo "📦 步骤 1/3: 安装前端依赖..."
cd frontend

if [ -d "node_modules" ]; then
    echo "   清理旧的依赖..."
    rm -rf node_modules package-lock.json
fi

echo "   安装依赖包（这可能需要几分钟）..."
npm install

if [ $? -eq 0 ]; then
    echo "   ✅ 前端依赖安装成功"
else
    echo "   ❌ 前端依赖安装失败"
    exit 1
fi

cd ..
echo ""

# 2. 检查环境变量
echo "🔑 步骤 2/3: 检查环境变量..."
if [ ! -f ".env" ]; then
    echo "   创建 .env 文件..."
    cp .env.example .env
    echo "   ⚠️  请编辑 .env 文件并设置必要的密钥"
else
    echo "   ✅ .env 文件已存在"
fi
echo ""

# 3. 验证Python依赖
echo "🐍 步骤 3/3: 检查Python依赖..."
if command -v python &> /dev/null; then
    PYTHON_CMD=python
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "   ❌ Python 未安装"
    exit 1
fi

echo "   Python 版本: $($PYTHON_CMD --version)"

if $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo "   ✅ FastAPI 已安装"
else
    echo "   ⚠️  FastAPI 未安装，运行: pip install -r requirements.txt"
fi

echo ""
echo "========================================"
echo "✅ 修复完成！"
echo ""
echo "📝 下一步："
echo "   1. 编辑 .env 文件设置密钥"
echo "   2. 启动后端: uvicorn app.main:app --reload"
echo "   3. 启动前端: cd frontend && npm run dev"
echo ""
echo "或者使用 Docker:"
echo "   ./start.sh"
echo ""
