# PayGuard 问题修复脚本 (Windows PowerShell)

Write-Host "🔧 PayGuard 问题修复脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Node.js
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js 未安装，请先安装 Node.js" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Node.js 版本: $(node --version)" -ForegroundColor Green
Write-Host ""

# 1. 修复前端依赖
Write-Host "📦 步骤 1/3: 安装前端依赖..." -ForegroundColor Yellow
Set-Location frontend

if (Test-Path "node_modules") {
    Write-Host "   清理旧的依赖..." -ForegroundColor Gray
    Remove-Item -Recurse -Force node_modules, package-lock.json -ErrorAction SilentlyContinue
}

Write-Host "   安装依赖包（这可能需要几分钟）..." -ForegroundColor Gray
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ 前端依赖安装成功" -ForegroundColor Green
} else {
    Write-Host "   ❌ 前端依赖安装失败" -ForegroundColor Red
    exit 1
}

Set-Location ..
Write-Host ""

# 2. 检查环境变量
Write-Host "🔑 步骤 2/3: 检查环境变量..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "   创建 .env 文件..." -ForegroundColor Gray
    Copy-Item .env.example .env
    Write-Host "   ⚠️  请编辑 .env 文件并设置必要的密钥" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ .env 文件已存在" -ForegroundColor Green
}
Write-Host ""

# 3. 验证Python依赖
Write-Host "🐍 步骤 3/3: 检查Python依赖..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "   Python 版本: $pythonVersion" -ForegroundColor Gray

    python -c "import fastapi" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ FastAPI 已安装" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  FastAPI 未安装，运行: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Python 未安装" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ 修复完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 下一步：" -ForegroundColor Cyan
Write-Host "   1. 编辑 .env 文件设置密钥"
Write-Host "   2. 启动后端: uvicorn app.main:app --reload"
Write-Host "   3. 启动前端: cd frontend; npm run dev"
Write-Host ""
Write-Host "或者使用 Docker:"
Write-Host "   .\start.sh"
Write-Host ""
