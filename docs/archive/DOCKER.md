# PayGuard Docker Deployment Guide

完整的Docker容器化部署文档

## 📦 项目Docker化架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │  Frontend   │   │   Backend   │   │  PostgreSQL │       │
│  │   (Nginx)   │──▶│   (FastAPI) │──▶│     DB      │       │
│  │   Port 80   │   │  Port 8000  │   │  Port 5432  │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│                            │                                  │
│                            ▼                                  │
│                    ┌─────────────┐                           │
│                    │    Redis    │                           │
│                    │   (Cache)   │                           │
│                    │  Port 6379  │                           │
│                    └─────────────┘                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 1. 克隆项目

```bash
git clone <repository-url>
cd payguard_crew_starter
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要！）
nano .env  # 或使用你喜欢的编辑器
```

**必须修改的配置项：**
- `JWT_SECRET_KEY` - JWT密钥（生产环境必须修改）
- `POSTGRES_PASSWORD` - 数据库密码
- `REDIS_PASSWORD` - Redis密码
- `API_KEY_ADMIN` - 管理员API密钥
- `OPENAI_API_KEY` - OpenAI API密钥（如果使用LLM功能）

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 访问应用

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health/health

### 5. 登录测试

- 管理员: `admin` / `admin123`
- 分析师: `demo` / `demo123`

## 📋 Docker Compose 配置

### 生产环境（推荐）

```bash
# 使用完整配置启动
docker-compose -f docker-compose.yml up -d
```

包含的服务：
- ✅ PostgreSQL 数据库
- ✅ Redis 缓存
- ✅ Backend API (FastAPI)
- ✅ Frontend (Vue + Nginx)

### 开发环境

```bash
# 使用开发配置启动（带热重载）
docker-compose -f docker-compose.dev.yml up
```

特性：
- 🔥 代码热重载
- 📁 本地目录挂载
- 🐛 调试模式
- 💾 SQLite数据库（无需PostgreSQL）

### 生产环境（带扩展）

```bash
# 使用生产配置启动（带资源限制和副本）
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

增强特性：
- 🔒 资源限制（CPU/内存）
- 📈 Backend副本（2个实例）
- 📝 日志管理
- 🔄 自动重启策略

## 🛠️ 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f

# 查看最近100行
docker-compose logs --tail=100

# 查看特定服务
docker-compose logs -f backend frontend
```

### 数据库管理

```bash
# 进入PostgreSQL容器
docker-compose exec postgres psql -U payguard -d payguard

# 备份数据库
docker-compose exec postgres pg_dump -U payguard payguard > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U payguard payguard < backup.sql

# 查看数据库大小
docker-compose exec postgres psql -U payguard -c "\l+"
```

### Redis管理

```bash
# 进入Redis CLI
docker-compose exec redis redis-cli -a redis_secret_2024

# 查看Redis信息
docker-compose exec redis redis-cli -a redis_secret_2024 INFO

# 清空缓存
docker-compose exec redis redis-cli -a redis_secret_2024 FLUSHALL
```

### 清理与重建

```bash
# 停止并删除容器、网络
docker-compose down

# 停止并删除容器、网络、卷（⚠️ 会删除数据）
docker-compose down -v

# 重新构建镜像
docker-compose build

# 强制重新构建并启动
docker-compose up -d --build

# 清理未使用的镜像
docker image prune -a
```

## 🔧 故障排查

### 1. 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看详细日志
docker-compose logs <service-name>

# 检查配置
docker-compose config
```

### 2. 端口冲突

```bash
# 查看端口占用
# Linux/Mac
lsof -i :8000
netstat -tulpn | grep 8000

# Windows
netstat -ano | findstr 8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"  # 改为8001
```

### 3. 数据库连接失败

```bash
# 检查PostgreSQL健康状态
docker-compose exec postgres pg_isready -U payguard

# 检查连接字符串
docker-compose exec backend env | grep DATABASE_URL

# 重启数据库
docker-compose restart postgres
```

### 4. 前端无法访问后端

```bash
# 检查网络连接
docker-compose exec frontend ping backend

# 检查Nginx配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 重新加载Nginx配置
docker-compose exec frontend nginx -s reload
```

### 5. 内存不足

```bash
# 查看资源使用
docker stats

# 增加Docker内存限制（Docker Desktop）
# Settings -> Resources -> Memory -> 4GB+

# 使用资源限制配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 监控与维护

### 健康检查

```bash
# 检查所有服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost:8000/api/health/health
curl http://localhost/
```

### 资源监控

```bash
# 实时监控
docker stats

# 查看磁盘使用
docker system df

# 清理磁盘空间
docker system prune -a --volumes
```

### 备份策略

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U payguard payguard > backup_${DATE}.sql
tar -czf data_backup_${DATE}.tar.gz data/ logs/
echo "Backup completed: backup_${DATE}.sql data_backup_${DATE}.tar.gz"
EOF

chmod +x backup.sh
./backup.sh
```

## 🔐 安全最佳实践

### 1. 环境变量安全

```bash
# 不要提交.env到Git
echo ".env" >> .gitignore

# 使用强密码
openssl rand -hex 32  # 生成随机密钥
```

### 2. 网络安全

```bash
# 限制对外暴露的端口
# 只暴露必要的端口（80, 443）
# 数据库和Redis不对外暴露

# 使用内部网络
networks:
  payguard-network:
    internal: true  # 仅内部通信
```

### 3. 容器安全

```bash
# 使用非root用户运行
USER appuser

# 只读文件系统
read_only: true

# 限制capabilities
cap_drop:
  - ALL
```

## 🚢 生产部署清单

- [ ] 修改所有默认密码
- [ ] 配置SSL证书（HTTPS）
- [ ] 设置正确的CORS_ORIGINS
- [ ] 配置日志轮转
- [ ] 设置备份策略
- [ ] 配置监控告警
- [ ] 启用防火墙规则
- [ ] 设置资源限制
- [ ] 配置域名DNS
- [ ] 测试灾难恢复流程

## 📈 扩展与优化

### 水平扩展

```bash
# 扩展Backend副本
docker-compose up -d --scale backend=3

# 添加负载均衡（需要额外配置Nginx）
```

### 性能优化

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 持久化存储

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: /path/to/persistent/storage
      o: bind
```

## 🆘 获取帮助

- 查看日志: `docker-compose logs -f`
- 检查配置: `docker-compose config`
- 官方文档: https://docs.docker.com/
- 项目文档: 查看 `README.md`

## 📝 更新日志

### v1.0.0 (2026-07-09)
- ✅ 初始Docker配置
- ✅ 多阶段构建优化
- ✅ 健康检查配置
- ✅ 开发/生产环境分离
- ✅ 完整文档

---

**记住**: 生产环境部署前，务必修改所有默认密码和密钥！
