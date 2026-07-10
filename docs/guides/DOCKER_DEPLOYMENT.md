# PayGuard Docker 部署完整指南

## 📋 目录

1. [部署方式对比](#部署方式对比)
2. [快速开始](#快速开始)
3. [开发环境部署](#开发环境部署)
4. [生产环境部署](#生产环境部署)
5. [配置说明](#配置说明)
6. [故障排除](#故障排除)

---

## 🎯 部署方式对比

| 特性 | 简单模式 | 开发模式 | 完整模式 | 生产模式 |
|------|---------|---------|---------|---------|
| **文件** | `docker-compose.yml` | `docker-compose.dev.yml` | `docker-compose.full.yml` | `docker-compose.prod.yml` |
| **数据库** | SQLite | SQLite | PostgreSQL | PostgreSQL |
| **缓存** | - | - | Redis | Redis |
| **热重载** | ❌ | ✅ | ❌ | ❌ |
| **副本数** | 1 | 1 | 1 | 2+ |
| **资源限制** | ❌ | ❌ | ❌ | ✅ |
| **适用场景** | 快速演示 | 本地开发 | 测试环境 | 生产部署 |

---

## 🚀 快速开始

### 方式1：简单模式（最快）

```bash
# 1. 启动后端
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 访问
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

**特点**：
- ✅ 一键启动，无需配置
- ✅ 使用SQLite，无额外依赖
- ✅ 适合快速演示和测试

---

## 💻 开发环境部署

### 使用 docker-compose.dev.yml

```bash
# 1. 启动开发环境（前端+后端）
docker-compose -f docker-compose.dev.yml up

# 2. 实时查看日志
docker-compose -f docker-compose.dev.yml logs -f backend frontend

# 3. 访问
# 后端: http://localhost:8000
# 前端: http://localhost:3000
```

### 特点

- ✅ **代码热重载** - 修改代码立即生效
- ✅ **前后端分离** - 独立开发调试
- ✅ **使用SQLite** - 无需配置数据库
- ✅ **调试模式** - 详细错误信息

### 开发工作流

```bash
# 修改后端代码
vi app/api/audit.py
# uvicorn自动重载，无需重启

# 修改前端代码
vi frontend/src/views/Dashboard.vue
# Vite HMR自动更新，无需刷新

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

---

## 🏭 生产环境部署

### 方式1：完整模式（推荐）

使用 `docker-compose.full.yml` - 包含PostgreSQL和Redis

#### 步骤1：配置环境变量

```bash
# 创建.env文件
cat > .env <<EOF
# 数据库配置
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here

# JWT密钥（必须修改）
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# API密钥
API_KEYS=prod-api-key-2024

# LLM配置（可选）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_MODEL=deepseek-chat

# 或使用OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-openai-key
# OPENAI_MODEL=gpt-4o-mini

# CrewAI配置
ENABLE_CREWAI=false
EOF
```

#### 步骤2：构建并启动

```bash
# 1. 构建镜像
docker-compose -f docker-compose.full.yml build

# 2. 启动所有服务
docker-compose -f docker-compose.full.yml up -d

# 3. 检查服务状态
docker-compose -f docker-compose.full.yml ps

# 4. 查看日志
docker-compose -f docker-compose.full.yml logs -f
```

#### 步骤3：验证部署

```bash
# 检查后端健康状态
curl http://localhost:8000/api/health/health

# 检查前端
curl http://localhost/

# 检查数据库连接
docker-compose -f docker-compose.full.yml exec backend python -c "from app.db.database import engine; print('DB OK')"
```

#### 访问地址

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health/health

---

### 方式2：生产模式（高可用）

使用 `docker-compose.prod.yml` - 添加资源限制和副本

```bash
# 1. 组合配置文件启动
docker-compose \
  -f docker-compose.full.yml \
  -f docker-compose.prod.yml \
  up -d

# 2. 查看副本状态
docker-compose -f docker-compose.full.yml -f docker-compose.prod.yml ps

# 3. 扩展后端副本
docker-compose -f docker-compose.full.yml -f docker-compose.prod.yml up -d --scale backend=3
```

**特点**：
- ✅ **负载均衡** - 2个后端副本
- ✅ **资源限制** - CPU/内存控制
- ✅ **日志轮转** - 自动清理旧日志
- ✅ **健康检查** - 自动重启故障容器
- ✅ **滚动更新** - 零停机部署

---

## ⚙️ 配置说明

### 环境变量清单

#### 必需变量（生产环境）

```bash
# 安全密钥（必须修改）
JWT_SECRET_KEY=<至少32位随机字符串>
API_KEYS=<API密钥，逗号分隔>

# 数据库密码
POSTGRES_PASSWORD=<强密码>
REDIS_PASSWORD=<强密码>
```

#### 可选变量

```bash
# 应用配置
APP_ENV=production                # 环境：dev/production
APP_NAME=payguard-crew           # 应用名称
APP_VERSION=0.2.0                # 版本号

# LLM配置
LLM_PROVIDER=disabled            # disabled/openai/deepseek/ollama
DEEPSEEK_API_KEY=                # DeepSeek API密钥
DEEPSEEK_MODEL=deepseek-chat     # 模型名称
OPENAI_API_KEY=                  # OpenAI API密钥
OPENAI_MODEL=gpt-4o-mini         # GPT模型
OLLAMA_MODEL=qwen2.5             # Ollama模型
OLLAMA_BASE_URL=http://...       # Ollama地址

# CrewAI
ENABLE_CREWAI=false              # 启用多Agent编排

# RAG配置
RAG_TOP_K=3                      # 检索文档数量
PAYGUARD_DOCS_DIR=/app/docs      # 知识库目录

# 限流配置
RATE_LIMIT_ENABLED=true          # 启用限流
RATE_LIMIT_PER_MINUTE=100        # 每分钟请求数

# 日志
LOG_LEVEL=INFO                   # DEBUG/INFO/WARNING/ERROR

# 前端配置
VITE_API_URL=http://localhost:8000  # API地址
```

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose -f docker-compose.full.yml up -d

# 停止所有服务
docker-compose -f docker-compose.full.yml down

# 重启特定服务
docker-compose -f docker-compose.full.yml restart backend

# 查看服务状态
docker-compose -f docker-compose.full.yml ps

# 查看资源使用
docker stats
```

### 日志查看

```bash
# 查看所有日志
docker-compose -f docker-compose.full.yml logs

# 实时跟踪日志
docker-compose -f docker-compose.full.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.full.yml logs backend
docker-compose -f docker-compose.full.yml logs postgres

# 查看最近100行
docker-compose -f docker-compose.full.yml logs --tail=100 backend
```

### 数据库管理

```bash
# 连接PostgreSQL
docker-compose -f docker-compose.full.yml exec postgres psql -U payguard -d payguard

# 备份数据库
docker-compose -f docker-compose.full.yml exec postgres pg_dump -U payguard payguard > backup.sql

# 恢复数据库
docker-compose -f docker-compose.full.yml exec -T postgres psql -U payguard payguard < backup.sql

# 查看数据库大小
docker-compose -f docker-compose.full.yml exec postgres psql -U payguard -c "\l+"
```

### 容器管理

```bash
# 进入后端容器
docker-compose -f docker-compose.full.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.full.yml exec frontend sh

# 执行Python脚本
docker-compose -f docker-compose.full.yml exec backend python scripts/check_health.py

# 清理未使用的资源
docker system prune -a --volumes
```

---

## 🐛 故障排除

### 问题1：容器无法启动

**症状**：`docker-compose up`后容器立即退出

```bash
# 查看详细日志
docker-compose -f docker-compose.full.yml logs backend

# 检查容器状态
docker-compose -f docker-compose.full.yml ps

# 常见原因：
# 1. 端口被占用
netstat -tulpn | grep 8000

# 2. 权限问题
sudo chown -R $USER:$USER data logs

# 3. 环境变量缺失
docker-compose -f docker-compose.full.yml config
```

### 问题2：数据库连接失败

**症状**：后端日志显示数据库连接错误

```bash
# 检查PostgreSQL是否就绪
docker-compose -f docker-compose.full.yml exec postgres pg_isready

# 检查连接字符串
docker-compose -f docker-compose.full.yml exec backend env | grep DATABASE_URL

# 手动测试连接
docker-compose -f docker-compose.full.yml exec backend python -c "
from app.db.database import engine
try:
    conn = engine.connect()
    print('Database connected!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
"
```

### 问题3：前端无法访问后端

**症状**：前端页面加载但API请求失败

```bash
# 检查网络连接
docker network ls
docker network inspect payguard-network

# 检查后端健康状态
curl http://localhost:8000/api/health/health

# 检查CORS配置
docker-compose -f docker-compose.full.yml logs backend | grep CORS

# 解决方案：
# 1. 确保前端环境变量正确
# VITE_API_URL=http://localhost:8000

# 2. 检查nginx配置（如果使用）
docker-compose -f docker-compose.full.yml exec frontend cat /etc/nginx/conf.d/default.conf
```

### 问题4：镜像构建失败

**症状**：`docker-compose build`报错

```bash
# 清理Docker缓存
docker builder prune -a

# 重新构建（不使用缓存）
docker-compose -f docker-compose.full.yml build --no-cache

# 检查Dockerfile语法
docker-compose -f docker-compose.full.yml config

# 常见原因：
# 1. 网络问题 - 使用国内镜像
# 2. 依赖版本冲突 - 检查requirements.txt
# 3. 磁盘空间不足 - df -h
```

### 问题5：容器内存不足

**症状**：容器被OOM Killer杀死

```bash
# 查看容器资源使用
docker stats

# 增加内存限制（docker-compose.prod.yml）
# deploy:
#   resources:
#     limits:
#       memory: 4G  # 增加到4G

# 或临时增加
docker-compose -f docker-compose.full.yml up -d --scale backend=1 --memory=4g
```

---

## 📊 性能优化

### 1. 使用多阶段构建

```dockerfile
# 已在Dockerfile中实现
# - dependencies阶段：安装依赖
# - final阶段：复制应用代码
# 优势：减小镜像体积50%+
```

### 2. 启用健康检查

```yaml
# 已配置在docker-compose中
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. 配置资源限制

```yaml
# 使用docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### 4. 日志管理

```yaml
# 已配置日志轮转
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 🔒 安全最佳实践

### 1. 使用非root用户

```dockerfile
# 已在Dockerfile中实现
RUN useradd -m -u 1000 payguard
USER payguard
```

### 2. 强密钥要求

```bash
# 生产环境必须设置
JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY is required in production}
```

### 3. 网络隔离

```yaml
# 使用独立网络
networks:
  payguard-network:
    driver: bridge
```

### 4. 数据持久化

```yaml
# 使用命名卷
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

---

## 📦 更新部署

### 滚动更新（零停机）

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose -f docker-compose.full.yml build

# 3. 滚动更新
docker-compose -f docker-compose.full.yml up -d --no-deps --build backend

# 4. 验证新版本
curl http://localhost:8000/ | jq .version
```

### 回滚部署

```bash
# 1. 查看镜像历史
docker images payguard-backend

# 2. 使用旧镜像
docker tag payguard-backend:old payguard-backend:latest

# 3. 重启服务
docker-compose -f docker-compose.full.yml up -d backend
```

---

## 🎯 部署检查清单

### 生产环境上线前

- [ ] 修改所有默认密钥和密码
- [ ] 配置HTTPS证书（推荐Let's Encrypt）
- [ ] 启用PostgreSQL和Redis
- [ ] 配置日志收集和监控
- [ ] 设置定期数据库备份
- [ ] 配置防火墙规则
- [ ] 测试健康检查端点
- [ ] 压力测试和性能验证
- [ ] 准备回滚方案
- [ ] 文档和运维手册

---

## 📞 获取帮助

遇到问题？

1. 查看日志：`docker-compose logs -f`
2. 检查健康状态：`curl http://localhost:8000/api/health/health`
3. 阅读文档：
   - [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南
   - [LLM_CONFIG_GUIDE.md](LLM_CONFIG_GUIDE.md) - LLM配置
   - [ISSUES_REPORT.md](ISSUES_REPORT.md) - 常见问题

---

**🎉 现在可以开始使用Docker部署PayGuard了！**
