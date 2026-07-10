# Docker 部署完整指南

> **版本**: v0.2.0  
> **更新**: 2026-07-10

---

## 📋 目录

- [快速开始](#快速开始)
- [部署模式](#部署模式)
- [开发环境](#开发环境)
- [生产环境](#生产环境)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ 可用内存
- 5GB+ 磁盘空间

### 一键部署

**Windows**:
```powershell
.\deploy.bat
```

**Linux/Mac**:
```bash
chmod +x deploy.sh
./deploy.sh
```

选择部署模式：
1. **开发模式** - 热重载、详细日志
2. **生产模式** - 性能优化、PostgreSQL

---

## 部署模式

### 开发模式 (Development)

**特点**:
- ✅ SQLite数据库（无需外部依赖）
- ✅ 前端热重载（Vite HMR）
- ✅ 后端自动重启（uvicorn --reload）
- ✅ 详细调试日志
- ✅ 演示数据预加载

**启动**:
```bash
# 使用 .env.development 配置
docker-compose -f docker-compose.yml up -d

# 或手动指定
docker-compose --env-file .env.development up -d
```

**访问地址**:
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

### 生产模式 (Production)

**特点**:
- ✅ PostgreSQL数据库（持久化）
- ✅ Redis缓存（速率限制）
- ✅ Nginx反向代理（负载均衡）
- ✅ 健康检查（自动重启）
- ✅ 日志持久化
- ✅ SSL/TLS支持

**启动**:
```bash
# 使用 .env.production 配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 或
docker-compose --env-file .env.production -f docker-compose.prod.yml up -d
```

**访问地址**:
- 统一入口: http://localhost （Nginx）
- 前端: http://localhost:80
- 后端API: http://localhost/api

---

## 开发环境

### 配置文件: .env.development

```env
# 环境模式
ENVIRONMENT=development

# 数据库（SQLite）
DATABASE_URL=sqlite:///./payguard.db

# Redis（可选，开发环境可不启用）
REDIS_HOST=redis
REDIS_PORT=6379

# API密钥（开发用）
API_KEYS=dev-key-123,test-key-456

# JWT密钥（开发用，32字符以上）
JWT_SECRET_KEY=dev-jwt-secret-key-minimum-32-characters

# CORS（开发允许所有）
CORS_ORIGINS=*

# LLM配置（可选）
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OPENAI_API_KEY=sk-xxx
```

### 容器架构

```yaml
services:
  backend:
    - SQLite数据库
    - 端口: 8000
    - 自动重启
  
  frontend:
    - Vite开发服务器
    - 端口: 3000
    - HMR热重载
```

### 开发工作流

```bash
# 1. 启动服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 3. 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 4. 重启服务
docker-compose restart backend

# 5. 停止服务
docker-compose down

# 6. 清理数据（谨慎！）
docker-compose down -v  # 删除卷
```

### 本地代码同步

代码挂载到容器，修改立即生效：

```yaml
volumes:
  - ./app:/app/app              # 后端代码
  - ./frontend/src:/app/src      # 前端代码
  - ./frontend/public:/app/public
```

**注意**: `node_modules` 和 `__pycache__` 不挂载，避免冲突。

---

## 生产环境

### 配置文件: .env.production

```env
# 环境模式
ENVIRONMENT=production

# 数据库（PostgreSQL）
DATABASE_URL=postgresql://payguard:your_password@postgres:5432/payguard

# Redis（必需）
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# API密钥（生产强密钥）
API_KEYS=prod-key-xxxxx,client-key-yyyyy

# JWT密钥（必须32字符以上，高强度）
JWT_SECRET_KEY=production-jwt-secret-key-must-be-very-strong-and-long

# CORS（严格限制）
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# 安全配置
ALLOWED_HOSTS=yourdomain.com,app.yourdomain.com
SSL_ENABLED=true

# LLM配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4
```

### 容器架构

```yaml
services:
  nginx:        # 反向代理
  backend:      # FastAPI应用
  frontend:     # Vue静态文件
  postgres:     # PostgreSQL数据库
  redis:        # Redis缓存
```

### 安全加固

#### 1. 密钥管理

```bash
# 生成强JWT密钥
openssl rand -base64 48

# 使用环境变量（不提交到Git）
export JWT_SECRET_KEY="your-strong-secret"
```

#### 2. PostgreSQL配置

```yaml
postgres:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # 从环境变量读取
  volumes:
    - postgres_data:/var/lib/postgresql/data  # 持久化
  networks:
    - internal  # 仅内部网络访问
```

#### 3. Nginx配置

```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    
    # HTTPS重定向
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    
    location /api {
        proxy_pass http://backend:8000;
    }
    
    location / {
        proxy_pass http://frontend:3000;
    }
}
```

### 部署检查清单

- [ ] 环境变量已配置（强密钥）
- [ ] CORS限制已设置（无通配符）
- [ ] SSL证书已安装
- [ ] 数据库密码已更改
- [ ] API密钥已更新
- [ ] 日志目录已挂载
- [ ] 备份策略已配置
- [ ] 监控告警已启用

---

## 配置说明

### 环境变量参考

| 变量 | 说明 | 开发默认 | 生产必需 |
|------|------|----------|----------|
| `ENVIRONMENT` | 运行模式 | development | production |
| `DATABASE_URL` | 数据库连接 | SQLite | PostgreSQL |
| `REDIS_HOST` | Redis地址 | - | 必需 |
| `API_KEYS` | API密钥列表 | 弱密钥 | 强密钥 |
| `JWT_SECRET_KEY` | JWT签名密钥 | 弱密钥 | 强密钥(32+字符) |
| `CORS_ORIGINS` | 允许的源 | * | 严格限制 |
| `LLM_PROVIDER` | LLM提供商 | ollama | openai/deepseek |

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| Frontend | 3000 | 3000 | Vue开发服务器 |
| Backend | 8000 | 8000 | FastAPI |
| Nginx | 80 | 80 | HTTP |
| Nginx | 443 | 443 | HTTPS |
| PostgreSQL | 5432 | - | 仅内部 |
| Redis | 6379 | - | 仅内部 |

### 数据持久化

```yaml
volumes:
  postgres_data:      # PostgreSQL数据
  redis_data:         # Redis持久化
  app_logs:           # 应用日志
  nginx_logs:         # Nginx日志
```

---

## 常见问题

### 1. 容器无法启动

```bash
# 查看日志
docker-compose logs backend

# 常见原因：
# - 端口已占用（修改docker-compose.yml端口）
# - 环境变量缺失（检查.env文件）
# - 内存不足（增加Docker内存限制）
```

### 2. 前端无法连接后端

**开发模式**:
```javascript
// frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api'
```

**生产模式**（通过Nginx）:
```javascript
const API_BASE_URL = '/api'  // 相对路径
```

### 3. 数据库连接失败

```bash
# 检查PostgreSQL是否启动
docker-compose ps postgres

# 进入容器测试连接
docker-compose exec backend python -c "from app.db.connection import test_connection; test_connection()"
```

### 4. LLM无法连接

**Ollama本地**:
```env
# Windows/Mac使用host.docker.internal
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Linux使用主机IP
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### 5. 权限问题

```bash
# Linux下可能需要修改权限
sudo chown -R $USER:$USER .
chmod -R 755 app frontend
```

### 6. 清理Docker空间

```bash
# 停止所有容器
docker-compose down

# 清理未使用的镜像
docker image prune -a

# 清理所有（谨慎！）
docker system prune -a --volumes
```

---

## 最佳实践

### 1. 使用多阶段构建

```dockerfile
# Dockerfile（生产优化）
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=frontend-builder /frontend/dist /app/static
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### 2. 健康检查

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3. 资源限制

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. 日志管理

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 网络隔离

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 仅内部通信
```

### 6. 密钥管理

```bash
# 使用Docker secrets（生产推荐）
echo "strong_password" | docker secret create postgres_password -

# 在compose中使用
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

### 7. 备份策略

```bash
# 数据库备份
docker-compose exec postgres pg_dump -U payguard payguard > backup_$(date +%Y%m%d).sql

# 恢复
docker-compose exec -T postgres psql -U payguard payguard < backup_20260710.sql
```

### 8. 监控和日志

```bash
# 实时日志
docker-compose logs -f --tail=100

# 特定服务
docker-compose logs -f backend

# 性能监控
docker stats
```

### 9. 滚动更新

```bash
# 零停机更新
docker-compose pull
docker-compose up -d --no-deps --build backend

# 分阶段更新
docker-compose up -d --scale backend=2
docker-compose stop backend_1
docker-compose up -d --scale backend=1
```

---

## 故障排除

### 服务无响应

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看资源使用
docker stats

# 3. 重启服务
docker-compose restart

# 4. 完全重建
docker-compose down
docker-compose up -d --build
```

### 性能问题

```bash
# 增加资源限制
docker-compose --compatibility up -d

# 检查慢查询
docker-compose exec postgres psql -U payguard -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

### 网络问题

```bash
# 检查网络
docker network ls
docker network inspect payguard_default

# 测试连通性
docker-compose exec backend ping frontend
```

---

## 相关文档

- [快速开始](QUICK_START.md)
- [环境配置](ENVIRONMENT_GUIDE.md)
- [API文档](../api/API_DOCUMENTATION.md)
- [故障排除](TROUBLESHOOTING.md)

---

**维护者**: PayGuard Team  
**更新**: 2026-07-10
