@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM PayGuard 一键Docker部署脚本 (Windows版本)
REM 用途：自动化部署整个系统（前端+后端+数据库）

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║          🚀 PayGuard 一键Docker部署 (Windows)             ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM 检查Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装
    echo 请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装
    echo 请先安装 Docker Compose
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo ✓ Docker 已安装: %DOCKER_VERSION%
echo ✓ Docker Compose 已安装
echo.

REM 选择部署模式
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 请选择部署模式：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1) 🚀 快速演示模式 (推荐)
echo      - 使用SQLite数据库
echo      - 单容器，快速启动
echo      - 适合：演示、测试
echo.
echo   2) 💻 开发模式
echo      - 代码热重载
echo      - 前后端分离
echo      - 适合：本地开发
echo.
echo   3) 🏭 完整生产模式
echo      - PostgreSQL + Redis
echo      - 前端 + 后端完整栈
echo      - 适合：测试、预发布、生产
echo.
set /p mode="请输入选项 (1/2/3) [默认: 1]: "
if "%mode%"=="" set mode=1

if "%mode%"=="1" (
    set MODE_NAME=快速演示模式
    set COMPOSE_FILE=docker-compose.yml
) else if "%mode%"=="2" (
    set MODE_NAME=开发模式
    set COMPOSE_FILE=docker-compose.dev.yml
) else if "%mode%"=="3" (
    set MODE_NAME=完整生产模式
    set COMPOSE_FILE=docker-compose.full.yml

    REM 检查环境变量
    if not exist ".env" (
        echo.
        echo ⚠️  未找到 .env 文件
        echo.
        set /p create_env="生产模式需要配置环境变量。是否自动创建？ (y/n) [默认: y]: "
        if "!create_env!"=="" set create_env=y

        if /i "!create_env!"=="y" (
            echo.
            echo 正在创建 .env 文件...
            copy .env.example .env >nul

            REM 生成随机密钥（简化版）
            set JWT_SECRET=change-this-jwt-secret-key-%RANDOM%%RANDOM%
            set POSTGRES_PASS=postgres_%RANDOM%%RANDOM%
            set REDIS_PASS=redis_%RANDOM%%RANDOM%

            REM 使用PowerShell替换（Windows更可靠）
            powershell -Command "(Get-Content .env) -replace 'your-super-secret-jwt-key-min-32-chars', '%JWT_SECRET%' | Set-Content .env"
            powershell -Command "(Get-Content .env) -replace 'your_secure_password_here', '%POSTGRES_PASS%' | Set-Content .env"
            powershell -Command "(Get-Content .env) -replace 'your_redis_password_here', '%REDIS_PASS%' | Set-Content .env"

            echo ✓ .env 文件已创建并配置随机密钥
            echo.
            echo ⚠️  重要：请编辑 .env 文件，配置以下项（可选）：
            echo   - LLM_PROVIDER（默认：disabled）
            echo   - DEEPSEEK_API_KEY / OPENAI_API_KEY（如需AI功能）
            echo.
            set /p edit_env="是否现在编辑 .env 文件？ (y/n) [默认: n]: "
            if /i "!edit_env!"=="y" (
                notepad .env
            )
        ) else (
            echo ❌ 生产模式需要 .env 文件
            pause
            exit /b 1
        )
    ) else (
        echo ✓ 已找到 .env 文件
    )
) else (
    echo ❌ 无效的选项
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 已选择: %MODE_NAME%
echo 配置文件: %COMPOSE_FILE%
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 清理旧容器（可选）
set /p clean="是否清理旧的容器和数据？ (y/n) [默认: n]: "
if /i "%clean%"=="y" (
    echo.
    echo 正在停止并删除旧容器...
    docker-compose -f %COMPOSE_FILE% down -v 2>nul
    echo ✓ 清理完成
    echo.
)

REM 构建镜像
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 步骤 1/3: 构建Docker镜像
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

docker-compose -f %COMPOSE_FILE% build
if %errorlevel% neq 0 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

echo.
echo ✓ 镜像构建完成
echo.

REM 启动服务
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 步骤 2/3: 启动服务
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

docker-compose -f %COMPOSE_FILE% up -d
if %errorlevel% neq 0 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)

echo.
echo ✓ 服务启动中...
echo.

REM 等待服务就绪
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 步骤 3/3: 等待服务就绪
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 等待后端健康检查
echo 等待后端启动
set /a counter=0
:wait_backend
set /a counter+=1
if %counter% gtr 30 goto wait_timeout

REM 使用curl检查（如果安装了）或者使用PowerShell
curl -sf http://localhost:8000/api/health/health >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✓ 后端服务就绪
    goto backend_ready
)

echo|set /p=.
timeout /t 2 /nobreak >nul
goto wait_backend

:wait_timeout
echo.
echo ⚠️  等待超时，但服务可能仍在启动中
goto show_status

:backend_ready

REM 显示服务状态
:show_status
echo.
echo 正在检查服务状态...
docker-compose -f %COMPOSE_FILE% ps

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║          ✅ 部署成功！                                     ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🌐 访问地址
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if "%mode%"=="1" (
    echo   后端API:     http://localhost:8000
    echo   API文档:     http://localhost:8000/docs
    echo   健康检查:    http://localhost:8000/api/health/health
) else if "%mode%"=="2" (
    echo   前端:        http://localhost:3000
    echo   后端API:     http://localhost:8000
    echo   API文档:     http://localhost:8000/docs
) else if "%mode%"=="3" (
    echo   前端:        http://localhost
    echo   后端API:     http://localhost:8000
    echo   API文档:     http://localhost:8000/docs
    echo   健康检查:    http://localhost:8000/api/health/health
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🔑 登录凭据
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   管理员:      admin / admin123
echo   分析师:      demo / demo123
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📚 常用命令
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   查看日志:    docker-compose -f %COMPOSE_FILE% logs -f
echo   停止服务:    docker-compose -f %COMPOSE_FILE% down
echo   重启服务:    docker-compose -f %COMPOSE_FILE% restart
echo   查看状态:    docker-compose -f %COMPOSE_FILE% ps
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📖 详细文档
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   快速开始:    QUICK_START.md
echo   Docker部署:  DOCKER_DEPLOYMENT.md
echo   LLM配置:     LLM_CONFIG_GUIDE.md
echo.
echo 🎉 现在可以开始使用 PayGuard 了！
echo.
pause
