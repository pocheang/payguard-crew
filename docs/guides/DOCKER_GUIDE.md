# PayGuard - 完整的Docker部署指南

## 🎯 快速开始（3分钟部署）

### 方式1：使用快速启动脚本（推荐）

```bash
# 1. 给脚本执行权限
chmod +x start.sh

# 2. 运行启动脚本
./start.sh

# 3. 按提示选择部署模式
#    1 - 开发模式（快速测试）
#    2 - 生产模式（完整功能）
```

### 方式2：手动启动

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env  # 编辑必要的配置

# 2. 启动所有服务
docker-compose up -d

# 3. 查看启动状态
docker-compose ps
docker-compose logs -f
```

## 📦 完整的Docker架构

```
PayGuard Docker Stack
├── Frontend (Nginx + Vue.js)     → Port 80
├── Backend (FastAPI + Python)    → Port 8000
├── PostgreSQL (Database)         → Port 5432
└── Redis (Cache)                 → Port 6379
```

## 🚀 部署方式

### 开发环境（Development）

适合：本地开发、快速测试

```bash
docker-compose -f docker-compose.dev.yml up
```

特性：
- ✅ 代码热重载
- ✅ SQLite数据库（无需PostgreSQL）
- ✅ 挂载本地代码目录
- ✅ 详细错误日志

### 生产环境（Production）

适合：正式部署、Demo演示

```bash
docker-compose up -d
```

包含：
- ✅ PostgreSQL 数据库
- ✅ Redis 缓存
- ✅ 健康检查
- ✅ 自动重启
- ✅ 资源限制

### 生产环境增强版

适合：大规模部署、高可用

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

增强：
- ✅ Backend 多副本（2个）
- ✅ CPU/内存限制
- ✅ 日志轮转
- ✅ 重启策略

## 📋 完整部署步骤

### 1. 环境准备

```bash
# 检查Docker版本
docker --version          # 需要 20.10+
docker-compose --version  # 需要 2.0+

# 检查系统资源
free -h                   # 至少 4GB RAM
df -h                     # 至少 10GB 磁盘空间
```

### 2. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 必须修改的配置（生产环境）
JWT_SECRET_KEY=your-secret-key-here-change-this
POSTGRES_PASSWORD=strong-password-here
REDIS_PASSWORD=strong-password-here
API_KEY_ADMIN=your-admin-api-key

# 可选配置
OPENAI_API_KEY=sk-xxx    # 如果使用LLM功能
DATABASE_TYPE=postgresql  # 或 sqlite
```

### 3. 启动服务

```bash
# 构建并启动
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f

# 等待所有服务健康
watch docker-compose ps
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 健康检查
curl http://localhost:8000/api/health/health
curl http://localhost/

# 查看日志
docker-compose logs backend
docker-compose logs frontend
```

### 5. 访问应用

- **前端**: http://localhost
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health/health

登录账号：
- 管理员: `admin` / `admin123`
- 分析师: `demo` / `demo123`

## 🛠️ 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 扩展服务副本
docker-compose up -d --scale backend=3
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f backend

# 最近100行
docker-compose logs --tail=100 backend
```

### 数据库操作

```bash
# 进入PostgreSQL
docker-compose exec postgres psql -U payguard -d payguard

# 备份数据库
docker-compose exec postgres pg_dump -U payguard payguard > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U payguard payguard

# 查看数据库大小
docker-compose exec postgres psql -U payguard -c "\l+"
```

### 清理与维护

```bash
# 停止并删除容器
docker-compose down

# 删除容器和数据卷（⚠️会删除数据）
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache

# 清理未使用的镜像
docker system prune -a

# 查看磁盘使用
docker system df
```

## 🔧 故障排查

### 问题1：端口被占用

```bash
# 查看端口占用
netstat -tulpn | grep 8000
lsof -i :80

# 解决方案1：停止占用进程
kill -9 <PID>

# 解决方案2：修改端口映射
# 编辑 docker-compose.yml
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题2：容器无法启动

```bash
# 查看详细错误
docker-compose logs <service-name>

# 检查配置语法
docker-compose config

# 重新构建
docker-compose build --no-cache <service-name>
```

### 问题3：数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose exec postgres pg_isready -U payguard

# 检查网络连接
docker-compose exec backend ping postgres

# 查看环境变量
docker-compose exec backend env | grep DATABASE
```

### 问题4：内存不足

```bash
# 查看资源使用
docker stats

# 增加Docker内存限制
# Docker Desktop: Settings → Resources → Memory

# 使用资源限制配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 监控与备份

### 实时监控

```bash
# 资源监控
docker stats

# 日志监控
docker-compose logs -f --tail=50

# 健康检查
watch -n 5 'docker-compose ps'
```

### 自动备份脚本

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups

# 备份数据库
docker-compose exec postgres pg_dump -U payguard payguard > backups/db_${DATE}.sql

# 备份数据文件
tar -czf backups/data_${DATE}.tar.gz data/ logs/

echo "Backup completed: backups/db_${DATE}.sql"
EOF

chmod +x backup.sh
./backup.sh
```

### 定时备份（Crontab）

```bash
# 每天凌晨2点备份
crontab -e
# 添加：
0 2 * * * cd /path/to/payguard && ./backup.sh
```

## 🔐 生产环境安全检查

### 必须修改的配置

- [ ] `JWT_SECRET_KEY` - 使用强随机密钥
- [ ] `POSTGRES_PASSWORD` - 使用强密码
- [ ] `REDIS_PASSWORD` - 使用强密码
- [ ] `API_KEY_ADMIN` - 使用随机生成的密钥
- [ ] 删除或禁用demo账号

### 生成安全密钥

```bash
# 生成JWT密钥
openssl rand -hex 32

# 生成随机密码
openssl rand -base64 24

# 生成API密钥
openssl rand -hex 16
```

### 网络安全

```bash
# 只暴露必要的端口
ports:
  - "80:80"      # 前端
  - "443:443"    # HTTPS（如需）
# PostgreSQL和Redis不对外暴露
```

## 📦 文件清单

```
payguard_crew_starter/
├── docker-compose.yml          # 生产环境配置
├── docker-compose.dev.yml      # 开发环境配置
├── docker-compose.prod.yml     # 生产增强配置
├── Dockerfile                  # 后端镜像
├── .dockerignore              # Docker忽略文件
├── .env.example               # 环境变量模板
├── start.sh                   # 快速启动脚本
├── DOCKER.md                  # Docker文档（本文件）
└── frontend/
    ├── Dockerfile             # 前端镜像
    ├── .dockerignore         # 前端忽略文件
    └── nginx.conf            # Nginx配置
```

## 🎯 部署检查清单

### 部署前

- [ ] 已安装Docker和Docker Compose
- [ ] 已配置.env文件
- [ ] 已修改默认密码
- [ ] 检查端口是否可用
- [ ] 准备充足的磁盘空间

### 部署后

- [ ] 所有容器正常运行
- [ ] 健康检查通过
- [ ] 前端可访问
- [ ] 后端API正常
- [ ] 数据库连接成功
- [ ] 可以正常登录

### 生产环境

- [ ] 配置HTTPS/SSL
- [ ] 设置域名解析
- [ ] 配置防火墙规则
- [ ] 启用日志轮转
- [ ] 设置备份策略
- [ ] 配置监控告警

## 🆘 获取帮助

1. **查看日志**: `docker-compose logs -f`
2. **检查状态**: `docker-compose ps`
3. **查看文档**: `cat DOCKER.md`
4. **健康检查**: `curl http://localhost:8000/api/health/health`

## 📚 相关文档

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [项目README](README.md)
- [前端文档](frontend/README.md)

---

**🎉 现在您的PayGuard已经完全Docker化，可以一键部署了！**
