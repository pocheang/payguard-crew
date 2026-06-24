# PowerShell 快速优化脚本
# quick-fix.ps1

Write-Host "🚀 PayGuard Crew 快速优化脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Python 版本
Write-Host "📋 1. 检查 Python 版本..." -ForegroundColor Yellow
python --version

# 2. 安装开发依赖
Write-Host ""
Write-Host "📦 2. 安装开发依赖..." -ForegroundColor Yellow
if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
    Write-Host "✅ 开发依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements-dev.txt 不存在，跳过" -ForegroundColor DarkYellow
}

# 3. 代码格式化
Write-Host ""
Write-Host "🎨 3. 代码格式化..." -ForegroundColor Yellow
try {
    black app/ tests/ --line-length 100
    Write-Host "✅ Black 格式化完成" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Black 未安装或执行失败，跳过格式化" -ForegroundColor DarkYellow
}

# 4. 代码检查
Write-Host ""
Write-Host "🔍 4. 代码语法检查..." -ForegroundColor Yellow
try {
    ruff check app/ tests/ --fix
    Write-Host "✅ Ruff 检查完成" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ruff 检查发现问题或未安装" -ForegroundColor DarkYellow
}

# 5. 运行测试
Write-Host ""
Write-Host "🧪 5. 运行测试..." -ForegroundColor Yellow
try {
    pytest tests/ -v --tb=short
    Write-Host "✅ 测试完成" -ForegroundColor Green
} catch {
    Write-Host "⚠️  部分测试失败或 Pytest 未安装" -ForegroundColor DarkYellow
}

# 6. 测试覆盖率
Write-Host ""
Write-Host "📊 6. 生成测试覆盖率报告..." -ForegroundColor Yellow
try {
    pytest --cov=app --cov-report=term-missing --cov-report=html
    Write-Host "✅ 覆盖率报告已生成到 htmlcov\index.html" -ForegroundColor Green
} catch {
    Write-Host "⚠️  覆盖率报告生成失败" -ForegroundColor DarkYellow
}

# 7. 依赖安全扫描
Write-Host ""
Write-Host "🔒 7. 依赖安全扫描..." -ForegroundColor Yellow
try {
    safety check
    Write-Host "✅ 安全扫描完成" -ForegroundColor Green
} catch {
    Write-Host "⚠️  发现安全问题或 Safety 未安装" -ForegroundColor DarkYellow
}

# 8. 类型检查
Write-Host ""
Write-Host "🔬 8. 类型检查..." -ForegroundColor Yellow
try {
    mypy app/ --ignore-missing-imports
    Write-Host "✅ 类型检查完成" -ForegroundColor Green
} catch {
    Write-Host "⚠️  发现类型问题或 Mypy 未安装" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ 快速优化完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 生成的文件：" -ForegroundColor Cyan
Write-Host "   - htmlcov\index.html (测试覆盖率报告)"
Write-Host ""
Write-Host "💡 下一步：" -ForegroundColor Cyan
Write-Host "   1. 查看测试覆盖率: Start-Process htmlcov\index.html"
Write-Host "   2. 启动服务: uvicorn app.main:app --reload"
Write-Host "   3. 查看 API 文档: http://127.0.0.1:8000/docs"
