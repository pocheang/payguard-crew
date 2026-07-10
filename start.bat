@echo off
REM PayGuard 完整启动脚本 (Windows)

echo ============================================
echo    PayGuard 支付风控系统 - 启动中...
echo ============================================
echo.

REM 检查虚拟环境
if not exist "venv\" (
    echo [错误] 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/5] 激活Python虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo [2/5] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
)

REM 初始化数据库
echo [3/5] 初始化数据库...
python -c "from app.db.database import init_db; from app.services.rule_service import init_rules_tables; init_db(); init_rules_tables(); print('数据库初始化完成')"

REM 启动后端服务
echo [4/5] 启动后端服务 (端口 8000)...
start "PayGuard Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端启动
echo [5/5] 等待后端启动...
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo [6/6] 启动前端服务 (端口 5173)...
cd frontend
start "PayGuard Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ============================================
echo    PayGuard 启动完成！
echo ============================================
echo.
echo  后端API: http://localhost:8000
echo  API文档: http://localhost:8000/docs
echo  前端界面: http://localhost:5173
echo.
echo  按 Ctrl+C 停止服务
echo ============================================
echo.

pause
