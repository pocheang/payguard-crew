.PHONY: help build up down restart logs ps clean dev prod demo test lint format

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
GREEN  := \033[0;32m
BLUE   := \033[0;34m
YELLOW := \033[1;33m
NC     := \033[0m

# ============================================
# 帮助信息
# ============================================

help: ## 显示帮助信息
	@echo ""
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║                                                           ║$(NC)"
	@echo "$(BLUE)║          PayGuard Docker 快速命令                          ║$(NC)"
	@echo "$(BLUE)║                                                           ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)快速启动:$(NC)"
	@echo "  make demo          - 快速演示模式（SQLite，单容器）"
	@echo "  make dev           - 开发模式（代码热重载）"
	@echo "  make prod          - 生产模式（PostgreSQL + Redis）"
	@echo ""
	@echo "$(GREEN)容器管理:$(NC)"
	@echo "  make up            - 启动所有服务"
	@echo "  make down          - 停止所有服务"
	@echo "  make restart       - 重启所有服务"
	@echo "  make ps            - 查看服务状态"
	@echo "  make logs          - 查看所有日志"
	@echo "  make logs-backend  - 查看后端日志"
	@echo "  make logs-frontend - 查看前端日志"
	@echo ""
	@echo "$(GREEN)构建与清理:$(NC)"
	@echo "  make build         - 构建所有镜像"
	@echo "  make clean         - 停止并删除所有容器和卷"
	@echo "  make clean-all     - 完全清理（包括镜像）"
	@echo ""
	@echo "$(GREEN)开发工具:$(NC)"
	@echo "  make test          - 运行测试"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"
	@echo "  make shell         - 进入后端容器"
	@echo "  make db-shell      - 进入数据库容器"
	@echo ""

# ============================================
# 快速启动命令
# ============================================

demo: ## 快速演示模式
	@echo "$(GREEN)启动快速演示模式...$(NC)"
	docker-compose -f docker-compose.yml up -d
	@echo ""
	@echo "$(GREEN)✓ 演示模式已启动！$(NC)"
	@echo "访问: http://localhost:8000"
	@echo "文档: http://localhost:8000/docs"

dev: ## 开发模式
	@echo "$(GREEN)启动开发模式...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "$(GREEN)✓ 开发模式已启动！$(NC)"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "文档: http://localhost:8000/docs"

prod: check-env ## 生产模式
	@echo "$(GREEN)启动生产模式...$(NC)"
	docker-compose -f docker-compose.full.yml up -d
	@echo ""
	@echo "$(GREEN)✓ 生产模式已启动！$(NC)"
	@echo "前端: http://localhost"
	@echo "后端: http://localhost:8000"
	@echo "文档: http://localhost:8000/docs"

check-env: ## 检查环境变量
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  .env 文件不存在，正在从 .env.example 创建...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env 文件已创建，请编辑配置后再次运行$(NC)"; \
		exit 1; \
	fi

# ============================================
# Docker 容器管理
# ============================================

up: ## 启动服务（默认使用 docker-compose.yml）
	docker-compose up -d

down: ## 停止服务
	docker-compose down

restart: ## 重启服务
	docker-compose restart

ps: ## 查看服务状态
	docker-compose ps

build: ## 构建镜像
	docker-compose build

logs: ## 查看所有日志
	docker-compose logs -f

logs-backend: ## 查看后端日志
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	docker-compose logs -f frontend

logs-db: ## 查看数据库日志
	docker-compose logs -f postgres

# ============================================
# 清理命令
# ============================================

clean: ## 停止并删除容器和卷
	@echo "$(YELLOW)正在清理容器和数据...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)✓ 清理完成$(NC)"

clean-all: ## 完全清理（包括镜像）
	@echo "$(YELLOW)正在完全清理...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)✓ 完全清理完成$(NC)"

# ============================================
# 开发工具
# ============================================

shell: ## 进入后端容器
	docker-compose exec backend bash

shell-frontend: ## 进入前端容器
	docker-compose exec frontend sh

db-shell: ## 进入数据库容器（PostgreSQL）
	docker-compose exec postgres psql -U payguard -d payguard

redis-cli: ## 进入 Redis CLI
	docker-compose exec redis redis-cli

# ============================================
# 测试与代码质量
# ============================================

test: ## 运行测试
	docker-compose exec backend pytest tests/ -v

test-cov: ## 运行测试并生成覆盖率报告
	docker-compose exec backend pytest tests/ -v --cov=app --cov-report=html

lint: ## 代码检查
	docker-compose exec backend ruff check app/
	docker-compose exec backend mypy app/

format: ## 代码格式化
	docker-compose exec backend ruff format app/
	docker-compose exec backend ruff check --fix app/

# ============================================
# 数据库管理
# ============================================

db-migrate: ## 运行数据库迁移
	docker-compose exec backend alembic upgrade head

db-rollback: ## 回滚数据库迁移
	docker-compose exec backend alembic downgrade -1

db-reset: ## 重置数据库（危险操作！）
	@echo "$(YELLOW)⚠️  这将删除所有数据！$(NC)"
	@read -p "确定要继续吗？(y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose exec backend alembic upgrade head; \
		echo "$(GREEN)✓ 数据库已重置$(NC)"; \
	fi

# ============================================
# 监控与健康检查
# ============================================

health: ## 检查服务健康状态
	@echo "$(GREEN)检查服务健康状态...$(NC)"
	@curl -sf http://localhost:8000/api/health/health && echo "$(GREEN)✓ 后端服务正常$(NC)" || echo "$(YELLOW)✗ 后端服务异常$(NC)"
	@curl -sf http://localhost/ > /dev/null && echo "$(GREEN)✓ 前端服务正常$(NC)" || echo "$(YELLOW)✗ 前端服务异常$(NC)"

stats: ## 查看容器资源使用情况
	docker stats --no-stream

# ============================================
# 备份与恢复
# ============================================

backup-db: ## 备份数据库
	@echo "$(GREEN)正在备份数据库...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U payguard payguard > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ 数据库备份完成$(NC)"

restore-db: ## 恢复数据库（需要指定文件：make restore-db FILE=backup.sql）
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)请指定备份文件：make restore-db FILE=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)正在恢复数据库...$(NC)"
	docker-compose exec -T postgres psql -U payguard payguard < $(FILE)
	@echo "$(GREEN)✓ 数据库恢复完成$(NC)"

# ============================================
# 其他工具
# ============================================

prune: ## 清理未使用的 Docker 资源
	docker system prune -af --volumes

version: ## 显示版本信息
	@echo "PayGuard Version: 0.2.0"
	@docker --version
	@docker-compose --version

install-deps: ## 安装依赖（本地开发）
	pip install -r requirements.txt
	cd frontend && npm install
