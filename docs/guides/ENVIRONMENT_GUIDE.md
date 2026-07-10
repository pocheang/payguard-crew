# PayGuard 环境配置指南

## 📋 环境说明

PayGuard 支持两种独立的环境配置：

- **开发环境 (Development)** - 用于本地开发和测试
- **生产环境 (Production)** - 用于正式部署和运行

---

## 🔄 环境切换

### 方式一：手动切换（推荐）

```bash
# 切换到开发环境
cp .env.development .env

# 切换到生产环境
cp .env.production .env
```

### 方式二：使用部署脚本

部署脚本会根据选择的模式自动使用对应的配置：

```bash
# Windows
deploy.bat

# Linux/Mac
./deploy.sh
```

### 方式三：直接指定环境文件

```bash
# 使用开发环境配置启动
docker-compose --env-file .env.development -f docker-compose.dev.yml up -d

# 使用生产环境配置启动
docker-compose --env-file .env.production -f docker-compose.full.yml up -d
```

---

## 🎯 环境对比

| 配置项 | 开发环境 | 生产环境 |
|--------|---------|---------|
| **基础配置** | | |
| APP_ENV | `development` | `production` |
| DEBUG | `true` | `false` |
| 日志级别 | `DEBUG` | `INFO` |
| **数据库** | | |
| 数据库类型 | SQLite | PostgreSQL |
| Redis | 可选（不使用） | 必需 |
| **安全配置** | | |
| JWT 过期时间 | 24小时 | 30分钟 |
| CORS | 允许所有本地源 | 仅允许指定域名 |
| 速率限制 | 关闭/宽松 | 严格启用 |
| API 密钥 | 固定测试值 | 强随机密钥 |
| **功能配置** | | |
| 错误详情显示 | ✅ 显示 | ❌ 隐藏 |
| SQL 查询日志 | ✅ 显示 | ❌ 关闭 |
| 热重载 | ✅ 启用 | ❌ 禁用 |
| 监控追踪 | 可选 | 推荐启用 |

---

## 🔧 开发环境 (Development)

### 特点

- **快速启动** - 使用 SQLite，无需额外安装数据库
- **便于调试** - 详细的日志输出和错误信息
- **宽松配置** - 长时效 token、宽松的限流和 CORS
- **节省成本** - 默认禁用 AI 功能

### 配置文件

[.env.development](.env.development)

### 快速开始

```bash
# 1. 复制配置文件
cp .env.development .env

# 2. 启动服务（选择一种方式）
make dev                                    # 使用 Makefile
docker-compose -f docker-compose.dev.yml up -d   # 直接使用 Docker Compose

# 3. 访问服务
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 默认凭据

```
API Key: demo-test-key-12345
用户名: admin / demo
密码: admin123 / demo123
```

### 可选配置

如需测试 AI 功能，编辑 `.env` 文件：

```bash
# 使用本地 Ollama（推荐开发环境）
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1

# 或使用 DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
```

---

## 🏭 生产环境 (Production)

### 特点

- **高性能** - PostgreSQL + Redis 架构
- **高安全** - 严格的认证、加密和限流
- **可监控** - 支持 Sentry、OpenTelemetry 等监控
- **高可用** - 支持多副本、负载均衡

### 配置文件

[.env.production](.env.production)

### 部署步骤

#### 1. 复制配置文件

```bash
cp .env.production .env
```

#### 2. 修改安全配置（必需！）

编辑 `.env` 文件，修改以下关键配置：

```bash
# JWT 密钥（生成强随机密钥）
JWT_SECRET_KEY=<生成的随机密钥>

# 数据库密码
POSTGRES_PASSWORD=<强密码>

# Redis 密码
REDIS_PASSWORD=<强密码>

# API 密钥
API_KEYS=<生产环境专用密钥>

# CORS 域名（仅允许实际域名）
CORS_ORIGINS=https://your-frontend-domain.com
```

#### 3. 生成安全密钥

**JWT 密钥**:
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

**数据库密码**:
```bash
# 生成 16 位随机密码
openssl rand -base64 16
```

#### 4. 启动服务

```bash
# 使用 Makefile
make prod

# 或使用 Docker Compose
docker-compose -f docker-compose.full.yml up -d

# 或使用部署脚本
./deploy.sh  # 选择模式 3（生产模式）
```

#### 5. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查健康状态
curl http://localhost:8000/api/health/health

# 查看日志
docker-compose logs -f
```

---

## 🔒 生产环境安全检查清单

部署到生产环境前，请确认：

### 必需项

- [ ] **JWT_SECRET_KEY** 已修改为强随机密钥（至少32字符）
- [ ] **POSTGRES_PASSWORD** 已修改为强密码
- [ ] **REDIS_PASSWORD** 已修改为强密码
- [ ] **API_KEYS** 已修改为生产环境专用密钥
- [ ] **CORS_ORIGINS** 仅包含实际的前端域名
- [ ] **DEBUG=false** 已确认
- [ ] **LOG_LEVEL=INFO** 或 WARNING
- [ ] **RATE_LIMIT_ENABLED=true** 已启用

### 推荐项

- [ ] 配置 **SSL/HTTPS** 证书
- [ ] 启用 **Sentry** 错误追踪
- [ ] 配置 **定期数据库备份**
- [ ] 设置 **监控告警**
- [ ] 配置 **防火墙规则**
- [ ] 启用 **日志轮转**
- [ ] 配置 **域名和 DNS**
- [ ] 测试 **灾难恢复流程**

---

## 🛠️ 常见配置场景

### 场景 1：本地开发（不需要 AI 功能）

```bash
# 使用开发环境配置
cp .env.development .env

# 确认 LLM 配置
LLM_PROVIDER=disabled

# 启动开发模式
make dev
```

### 场景 2：本地开发（需要测试 AI 功能）

```bash
# 使用开发环境配置
cp .env.development .env

# 编辑 .env，启用 Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1

# 先启动 Ollama
# 然后启动服务
make dev
```

### 场景 3：内网测试环境

```bash
# 使用生产环境配置作为基础
cp .env.production .env

# 修改必要的安全配置
# 设置为测试环境的域名
CORS_ORIGINS=http://test-internal.company.com

# 可以适当放宽限流
RATE_LIMIT_PER_MINUTE=500

# 启动完整栈
docker-compose -f docker-compose.full.yml up -d
```

### 场景 4：生产环境（公网部署）

```bash
# 使用生产环境配置
cp .env.production .env

# 仔细修改所有安全配置（参考上面的安全检查清单）

# 配置 HTTPS
# 编辑 nginx/nginx.conf，取消 SSL 配置注释

# 启动服务
make prod

# 配置域名解析和防火墙
```

---

## 📊 环境迁移

### 从开发切换到生产

```bash
# 1. 备份开发数据（如果需要）
docker-compose exec backend python scripts/export_data.py > dev_data.json

# 2. 停止开发环境
docker-compose -f docker-compose.dev.yml down

# 3. 切换到生产配置
cp .env.production .env

# 4. 修改生产配置中的安全项

# 5. 启动生产环境
make prod

# 6. 导入数据（如果需要）
docker-compose exec -T backend python scripts/import_data.py < dev_data.json
```

---

## 🐛 故障排查

### 配置文件不生效

```bash
# 确认使用的配置文件
docker-compose config | grep -A 5 environment

# 重新加载配置
docker-compose down
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查数据库配置
echo $DATABASE_URL

# 检查 PostgreSQL 状态
docker-compose exec postgres pg_isready -U payguard

# 查看数据库日志
docker-compose logs postgres
```

### CORS 错误

```bash
# 检查 CORS 配置
grep CORS_ORIGINS .env

# 确保前端域名在允许列表中
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

---

## 📞 获取帮助

- **配置问题**: 查看 `.env.development` 和 `.env.production` 中的详细注释
- **部署问题**: 查看 [QUICK_START.md](QUICK_START.md)
- **Docker 问题**: 查看 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

**安全提示**: 永远不要将包含真实密钥的 `.env` 文件提交到版本控制系统！
