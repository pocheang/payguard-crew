#!/bin/bash

# PayGuard 一键Docker部署脚本
# 用途：自动化部署整个系统（前端+后端+数据库）

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          🚀 PayGuard 一键Docker部署                        ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker 已安装: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
echo -e "${GREEN}✓${NC} Docker Compose 已安装"
echo ""

# 选择部署模式
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "请选择部署模式："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1) 🚀 快速演示模式 (推荐)"
echo "     - 使用SQLite数据库"
echo "     - 单容器，快速启动"
echo "     - 适合：演示、测试"
echo ""
echo "  2) 💻 开发模式"
echo "     - 代码热重载"
echo "     - 前后端分离"
echo "     - 适合：本地开发"
echo ""
echo "  3) 🏭 完整生产模式"
echo "     - PostgreSQL + Redis"
echo "     - 前端 + 后端完整栈"
echo "     - 适合：测试、预发布、生产"
echo ""
echo -n "请输入选项 (1/2/3) [默认: 1]: "
read -r mode

# 默认值
mode=${mode:-1}

case $mode in
    1)
        MODE_NAME="快速演示模式"
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        MODE_NAME="开发模式"
        COMPOSE_FILE="docker-compose.dev.yml"
        ;;
    3)
        MODE_NAME="完整生产模式"
        COMPOSE_FILE="docker-compose.full.yml"

        # 检查环境变量
        if [ ! -f ".env" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  未找到 .env 文件${NC}"
            echo ""
            echo "生产模式需要配置环境变量。是否自动创建？ (y/n) [默认: y]"
            read -r create_env
            create_env=${create_env:-y}

            if [[ $create_env == "y" ]]; then
                echo ""
                echo "正在创建 .env 文件..."
                cp .env.example .env

                # 生成随机密钥
                JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "change-this-jwt-secret-key-$(date +%s)")
                POSTGRES_PASS=$(openssl rand -base64 16 2>/dev/null || echo "postgres_$(date +%s)")
                REDIS_PASS=$(openssl rand -base64 16 2>/dev/null || echo "redis_$(date +%s)")

                # 更新 .env 文件
                sed -i.bak "s/your-super-secret-jwt-key-min-32-chars/$JWT_SECRET/" .env
                sed -i.bak "s/your_secure_password_here/$POSTGRES_PASS/" .env
                sed -i.bak "s/your_redis_password_here/$REDIS_PASS/" .env
                rm -f .env.bak

                echo -e "${GREEN}✓${NC} .env 文件已创建并配置随机密钥"
                echo ""
                echo -e "${YELLOW}重要：请编辑 .env 文件，配置以下项（可选）：${NC}"
                echo "  - LLM_PROVIDER（默认：disabled）"
                echo "  - DEEPSEEK_API_KEY / OPENAI_API_KEY（如需AI功能）"
                echo ""
                echo "是否现在编辑 .env 文件？ (y/n) [默认: n]"
                read -r edit_env
                if [[ $edit_env == "y" ]]; then
                    ${EDITOR:-nano} .env
                fi
            else
                echo -e "${RED}❌ 生产模式需要 .env 文件${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}✓${NC} 已找到 .env 文件"
        fi
        ;;
    *)
        echo -e "${RED}❌ 无效的选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "已选择: ${BLUE}$MODE_NAME${NC}"
echo "配置文件: $COMPOSE_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 清理旧容器（可选）
echo "是否清理旧的容器和数据？ (y/n) [默认: n]"
read -r clean
if [[ $clean == "y" ]]; then
    echo ""
    echo "正在停止并删除旧容器..."
    docker-compose -f $COMPOSE_FILE down -v 2>/dev/null || true
    echo -e "${GREEN}✓${NC} 清理完成"
    echo ""
fi

# 构建镜像
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/3: 构建Docker镜像"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker-compose -f $COMPOSE_FILE build

echo ""
echo -e "${GREEN}✓${NC} 镜像构建完成"
echo ""

# 启动服务
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/3: 启动服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker-compose -f $COMPOSE_FILE up -d

echo ""
echo -e "${GREEN}✓${NC} 服务启动中..."
echo ""

# 等待服务就绪
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/3: 等待服务就绪"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 等待后端健康检查
echo -n "等待后端启动"
for i in {1..30}; do
    if curl -sf http://localhost:8000/api/health/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} 后端服务就绪"
        break
    fi
    echo -n "."
    sleep 2
done

# 显示服务状态
echo ""
echo "正在检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║          ✅ 部署成功！                                     ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 访问地址"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [[ $mode == "1" ]]; then
    echo "  后端API:     http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
    echo "  健康检查:    http://localhost:8000/api/health/health"
elif [[ $mode == "2" ]]; then
    echo "  前端:        http://localhost:3000"
    echo "  后端API:     http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
elif [[ $mode == "3" ]]; then
    echo "  前端:        http://localhost"
    echo "  后端API:     http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
    echo "  健康检查:    http://localhost:8000/api/health/health"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 登录凭据"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  管理员:      admin / admin123"
echo "  分析师:      demo / demo123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 常用命令"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  查看日志:    docker-compose -f $COMPOSE_FILE logs -f"
echo "  停止服务:    docker-compose -f $COMPOSE_FILE down"
echo "  重启服务:    docker-compose -f $COMPOSE_FILE restart"
echo "  查看状态:    docker-compose -f $COMPOSE_FILE ps"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 详细文档"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  启动指南:    STARTUP_GUIDE.md"
echo "  Docker部署:  DOCKER_DEPLOYMENT.md"
echo "  LLM配置:     LLM_CONFIG_GUIDE.md"
echo ""
echo "🎉 现在可以开始使用 PayGuard 了！"
echo ""
