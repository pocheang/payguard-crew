# PayGuard 快速启动脚本 (PowerShell)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   PayGuard 支付风控系统 - 启动中..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "[错误] 虚拟环境不存在" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "[1/6] 激活Python虚拟环境..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# 检查依赖
Write-Host "[2/6] 检查Python依赖..." -ForegroundColor Green
$fastapi = pip show fastapi 2>$null
if (-not $fastapi) {
    Write-Host "[警告] 依赖未安装，正在安装..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 初始化数据库
Write-Host "[3/6] 初始化数据库..." -ForegroundColor Green
python -c "from app.db.database import init_db; from app.services.rule_service import init_rules_tables; init_db(); init_rules_tables(); print('✓ 数据库初始化完成')"

# 启动后端服务
Write-Host "[4/6] 启动后端服务 (端口 8000)..." -ForegroundColor Green
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru -WindowStyle Normal

# 等待后端启动
Write-Host "[5/6] 等待后端启动..." -ForegroundColor Green
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "[6/6] 启动前端服务 (端口 5173)..." -ForegroundColor Green
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   PayGuard 启动完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  后端API:   http://localhost:8000" -ForegroundColor White
Write-Host "  API文档:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  前端界面:  http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "  按 Ctrl+C 停止此脚本（服务会继续运行）" -ForegroundColor Yellow
Write-Host "  关闭服务请关闭对应的PowerShell窗口" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 保持脚本运行
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "脚本已停止" -ForegroundColor Yellow
}
