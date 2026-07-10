# PayGuard 快速启动指南

## 🚀 一键部署

PayGuard 支持三种部署模式，满足不同场景需求。

### 方式一：使用自动化脚本（推荐）

#### Windows 用户

```bash
# 双击运行或在命令行执行
deploy.bat
```

#### Linux/Mac 用户

```bash
# 添加执行权限并运行
chmod +x deploy.sh
./deploy.sh
```

### 方式二：使用 Makefile（开发者友好）

```bash
# 查看所有可用命令
make help

# 快速演示模式（推荐新手）
make demo

# 开发模式（适合开发）
make dev

# 生产模式（适合部署）
make prod
```

### 方式三：直接使用 Docker Compose

```bash
# 模式 1: 快速演示（SQLite，单容器）
docker-compose up -d

# 模式 2: 开发模式（代码热重载）
docker-compose -f docker-compose.dev.yml up -d

# 模式 3: 生产模式（PostgreSQL + Redis）
docker-compose -f docker-compose.full.yml up -d
```

---

## 📋 部署模式对比

| 特性 | 快速演示 | 开发模式 | 生产模式 |
|------|---------|---------|---------|
| **数据库** | SQLite | SQLite | PostgreSQL |
| **缓存** | - | - | Redis |
| **容器数** | 1个 | 2个 | 4个 |
| **启动速度** | ⚡ 最快 | 🔥 快 | 📦 中等 |
| **代码热重载** | ❌ | ✅ | ❌ |
| **适用场景** | 演示、测试 | 本地开发 | 生产环境 |
| **需要 .env** | ❌ | ❌ | ✅ |

---

## 🌐 访问地址

### 快速演示模式
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health/health

### 开发模式
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 生产模式
- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 🔑 默认登录凭据

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 分析师 | demo | demo123 |

⚠️ **生产环境请立即修改默认密码！**

---

## ⚙️ 环境配置

### 生产模式必需配置

生产模式需要配置 `.env` 文件：

```bash
# 1. 复制示例配置
cp .env.example .env

# 2. 编辑配置文件
nano .env  # 或使用你喜欢的编辑器

# 3. 必须修改的配置项
JWT_SECRET_KEY=<生成的随机密钥>
POSTGRES_PASSWORD=<数据库密码>
REDIS_PASSWORD=<Redis密码>
```

### 生成安全密钥

**JWT 密钥**:
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### 可选：AI 功能配置

如需启用AI功能，配置以下环境变量：

```bash
# 使用 DeepSeek（推荐，性价比高）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-api-key

# 或使用 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key

# 或使用本地 Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
```

---

## 📚 常用命令

### 使用 Makefile（推荐）

```bash
# 查看日志
make logs              # 所有服务
make logs-backend      # 仅后端
make logs-frontend     # 仅前端

# 容器管理
make ps                # 查看状态
make restart           # 重启服务
make down              # 停止服务

# 清理
make clean             # 清理容器和数据
make clean-all         # 完全清理（包括镜像）

# 进入容器
make shell             # 进入后端容器
make db-shell          # 进入数据库

# 健康检查
make health            # 检查服务状态
make stats             # 查看资源使用
```

### 使用 Docker Compose

```bash
# 查看日志
docker-compose logs -f
docker-compose logs -f backend

# 容器管理
docker-compose ps
docker-compose restart
docker-compose down

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U payguard -d payguard
```

---

## 🔍 故障排查

### 容器无法启动

```bash
# 检查容器状态
docker-compose ps

# 查看错误日志
docker-compose logs backend

# 检查端口占用
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

### 数据库连接失败

```bash
# 等待数据库就绪
docker-compose logs postgres

# 检查数据库健康状态
docker-compose exec postgres pg_isready -U payguard
```

### 健康检查失败

```bash
# 手动测试健康检查
curl http://localhost:8000/api/health/health

# 查看后端日志
docker-compose logs -f backend
```

### 重置环境

```bash
# 完全重置（会删除所有数据）
docker-compose down -v
rm -rf data/ logs/ .chroma/
docker-compose up -d
```

---

## 🎯 快速测试

### 1. 健康检查

```bash
curl http://localhost:8000/api/health/health
```

期望输出：
```json
{
  "status": "healthy",
  "version": "0.2.0"
}
```

### 2. 访问 API 文档

浏览器打开: http://localhost:8000/docs

### 3. 测试前端（开发/生产模式）

浏览器打开前端地址，使用默认凭据登录

---

## 🎬 API 测试示例

### 方式1：使用Swagger UI（最简单）

1. 打开浏览器：http://localhost:8000/docs
2. 找到 `POST /api/audit/transaction`
3. 点击 "Try it out"
4. 使用以下测试数据：

```json
{
  "transaction_id": "DEMO_TX_001",
  "user_id": "USER_DEMO",
  "merchant_id": "MERCHANT_DEMO",
  "amount": 500,
  "currency": "USD",
  "account_age_days": 365,
  "transaction_frequency_1h": 1,
  "ip_location_status": "normal",
  "device_status": "normal",
  "kyc_status": "verified",
  "merchant_risk_level": "low",
  "is_blacklisted": false,
  "timestamp": "2026-07-07T10:00:00"
}
```

5. 在 Headers 中添加：`x-api-key: demo-test-key-12345`
6. 点击 Execute

**预期结果**：
- 风险等级：low
- 自动通过
- 显示匹配的规则和证据

---

### 方式2：使用Curl命令

```bash
curl -X POST "http://localhost:8000/api/audit/transaction" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "CURL_TEST_001",
    "user_id": "USER_001",
    "merchant_id": "MERCHANT_001",
    "amount": 1000,
    "currency": "USD",
    "account_age_days": 100,
    "transaction_frequency_1h": 2,
    "ip_location_status": "normal",
    "device_status": "normal",
    "kyc_status": "verified",
    "merchant_risk_level": "low",
    "is_blacklisted": false,
    "timestamp": "2026-07-07T10:00:00"
  }'
```

---

## 📖 进阶使用

### 数据持久化

默认数据保存在以下目录：
- `./data/` - SQLite 数据库
- `./logs/` - 应用日志
- `./.chroma/` - 向量数据库
- `postgres_data/` - PostgreSQL 数据（生产模式）
- `redis_data/` - Redis 数据（生产模式）

### 数据库备份

```bash
# 使用 Makefile
make backup-db

# 手动备份
docker-compose exec -T postgres pg_dump -U payguard payguard > backup.sql
```

### 数据库恢复

```bash
# 使用 Makefile
make restore-db FILE=backup.sql

# 手动恢复
docker-compose exec -T postgres psql -U payguard payguard < backup.sql
```

---

## 🛡️ 安全建议

### 生产环境部署清单

- [ ] 修改默认密码
- [ ] 生成安全的 JWT 密钥
- [ ] 配置强密码（数据库、Redis）
- [ ] 配置 HTTPS/SSL（使用 nginx）
- [ ] 启用防火墙规则
- [ ] 配置 CORS 白名单
- [ ] 启用日志监控
- [ ] 定期备份数据
- [ ] 更新依赖版本

### SSL/HTTPS 配置

编辑 `nginx/nginx.conf` 取消 HTTPS 配置注释，并配置证书：

```bash
# 创建 SSL 目录
mkdir -p nginx/ssl

# 放置证书文件
# nginx/ssl/cert.pem
# nginx/ssl/key.pem

# 重启 nginx
docker-compose restart nginx
```

---

## 📞 获取帮助

- **文档**: 查看项目根目录下的其他 `.md` 文档
- **问题反馈**: 提交 GitHub Issue
- **配置问题**: 检查 `.env.example` 中的注释说明

---

## 🎉 下一步

1. ✅ 部署成功后，访问 API 文档了解接口
2. 📖 阅读 `DOCKER_DEPLOYMENT.md` 了解详细部署说明
3. 🔧 阅读 `LLM_CONFIG_GUIDE.md` 配置 AI 功能
4. 🏗️ 阅读 `README.md` 了解项目架构

---

**祝使用愉快！** 🎊
