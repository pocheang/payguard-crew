# PayGuard 一键Docker部署脚本 (Windows PowerShell)
# 用途：自动化部署整个系统（前端+后端+数据库）

$ErrorActionPreference = "Stop"

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "║          🚀 PayGuard 一键Docker部署                        ║" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker 未安装" -ForegroundColor Red
    Write-Host "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose 未安装" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker 已安装: $((docker --version).Split(' ')[2])" -ForegroundColor Green
Write-Host "✓ Docker Compose 已安装" -ForegroundColor Green
Write-Host ""

# 选择部署模式
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "请选择部署模式：" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1) 🚀 快速演示模式 (推荐)"
Write-Host "     - 使用SQLite数据库"
Write-Host "     - 单容器，快速启动"
Write-Host "     - 适合：演示、测试"
Write-Host ""
Write-Host "  2) 💻 开发模式"
Write-Host "     - 代码热重载"
Write-Host "     - 前后端分离"
Write-Host "     - 适合：本地开发"
Write-Host ""
Write-Host "  3) 🏭 完整生产模式"
Write-Host "     - PostgreSQL + Redis"
Write-Host "     - 前端 + 后端完整栈"
Write-Host "     - 适合：测试、预发布、生产"
Write-Host ""

$mode = Read-Host "请输入选项 (1/2/3) [默认: 1]"
if ([string]::IsNullOrWhiteSpace($mode)) { $mode = "1" }

switch ($mode) {
    "1" {
        $modeName = "快速演示模式"
        $composeFile = "docker-compose.yml"
    }
    "2" {
        $modeName = "开发模式"
        $composeFile = "docker-compose.dev.yml"
    }
    "3" {
        $modeName = "完整生产模式"
        $composeFile = "docker-compose.full.yml"

        # 检查环境变量
        if (!(Test-Path ".env")) {
            Write-Host ""
            Write-Host "⚠️  未找到 .env 文件" -ForegroundColor Yellow
            Write-Host ""
            $createEnv = Read-Host "生产模式需要配置环境变量。是否自动创建？ (y/n) [默认: y]"
            if ([string]::IsNullOrWhiteSpace($createEnv)) { $createEnv = "y" }

            if ($createEnv -eq "y") {
                Write-Host ""
                Write-Host "正在创建 .env 文件..." -ForegroundColor Gray
                Copy-Item .env.example .env

                # 生成随机密钥
                $jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
                $postgresPass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
                $redisPass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})

                # 更新 .env 文件
                (Get-Content .env) -replace 'your-super-secret-jwt-key-min-32-chars', $jwtSecret | Set-Content .env
                (Get-Content .env) -replace 'your_secure_password_here', $postgresPass | Set-Content .env
                (Get-Content .env) -replace 'your_redis_password_here', $redisPass | Set-Content .env

                Write-Host "✓ .env 文件已创建并配置随机密钥" -ForegroundColor Green
                Write-Host ""
                Write-Host "重要：请编辑 .env 文件，配置以下项（可选）：" -ForegroundColor Yellow
                Write-Host "  - LLM_PROVIDER（默认：disabled）"
                Write-Host "  - DEEPSEEK_API_KEY / OPENAI_API_KEY（如需AI功能）"
                Write-Host ""
                $editEnv = Read-Host "是否现在编辑 .env 文件？ (y/n) [默认: n]"
                if ($editEnv -eq "y") {
                    notepad .env
                }
            } else {
                Write-Host "❌ 生产模式需要 .env 文件" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "✓ 已找到 .env 文件" -ForegroundColor Green
        }
    }
    default {
        Write-Host "❌ 无效的选项" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "已选择: $modeName" -ForegroundColor Blue
Write-Host "配置文件: $composeFile"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# 清理旧容器（可选）
$clean = Read-Host "是否清理旧的容器和数据？ (y/n) [默认: n]"
if ($clean -eq "y") {
    Write-Host ""
    Write-Host "正在停止并删除旧容器..." -ForegroundColor Gray
    docker-compose -f $composeFile down -v 2>$null
    Write-Host "✓ 清理完成" -ForegroundColor Green
    Write-Host ""
}

# 构建镜像
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "步骤 1/3: 构建Docker镜像" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

docker-compose -f $composeFile build

Write-Host ""
Write-Host "✓ 镜像构建完成" -ForegroundColor Green
Write-Host ""

# 启动服务
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "步骤 2/3: 启动服务" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

docker-compose -f $composeFile up -d

Write-Host ""
Write-Host "✓ 服务启动中..." -ForegroundColor Green
Write-Host ""

# 等待服务就绪
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "步骤 3/3: 等待服务就绪" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# 等待后端健康检查
Write-Host "等待后端启动" -NoNewline
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "✓ 后端服务就绪" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
}

# 显示服务状态
Write-Host ""
Write-Host "正在检查服务状态..." -ForegroundColor Gray
docker-compose -f $composeFile ps

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║          ✅ 部署成功！                                     ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🌐 访问地址" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

switch ($mode) {
    "1" {
        Write-Host "  后端API:     http://localhost:8000"
        Write-Host "  API文档:     http://localhost:8000/docs"
        Write-Host "  健康检查:    http://localhost:8000/api/health/health"
    }
    "2" {
        Write-Host "  前端:        http://localhost:3000"
        Write-Host "  后端API:     http://localhost:8000"
        Write-Host "  API文档:     http://localhost:8000/docs"
    }
    "3" {
        Write-Host "  前端:        http://localhost"
        Write-Host "  后端API:     http://localhost:8000"
        Write-Host "  API文档:     http://localhost:8000/docs"
        Write-Host "  健康检查:    http://localhost:8000/api/health/health"
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔑 登录凭据" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  管理员:      admin / admin123"
Write-Host "  分析师:      demo / demo123"
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📚 常用命令" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  查看日志:    docker-compose -f $composeFile logs -f"
Write-Host "  停止服务:    docker-compose -f $composeFile down"
Write-Host "  重启服务:    docker-compose -f $composeFile restart"
Write-Host "  查看状态:    docker-compose -f $composeFile ps"
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📖 详细文档" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  启动指南:    STARTUP_GUIDE.md"
Write-Host "  Docker部署:  DOCKER_DEPLOYMENT.md"
Write-Host "  LLM配置:     LLM_CONFIG_GUIDE.md"
Write-Host ""
Write-Host "🎉 现在可以开始使用 PayGuard 了！" -ForegroundColor Green
Write-Host ""
