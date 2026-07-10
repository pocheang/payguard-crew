# PayGuard Docker 开发环境启动指南

## 🚀 快速启动

### 当前状态
- ✅ 环境配置：已复制 `.env.development`
- 🔄 Docker镜像：正在构建中...
- ⏳ 服务启动：等待镜像构建完成

---

## 📋 启动步骤

### 步骤 1：环境准备 ✅
```bash
# 已完成：复制开发环境配置
cp .env.development .env
```

### 步骤 2：构建镜像 🔄
```bash
# 正在执行：构建 Docker 镜像
docker-compose -f docker-compose.dev.yml build
```

**预计时间：3-5分钟**（首次构建）

### 步骤 3：启动服务 ⏳
```bash
# 等待执行：启动开发容器
docker-compose -f docker-compose.dev.yml up -d
```

### 步骤 4：验证服务 ⏳
```bash
# 检查容器状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

---

## 🌐 访问地址

构建完成后，服务将在以下地址可用：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://localhost:3000 | Vue.js 开发服务器 |
| **后端API** | http://localhost:8000 | FastAPI 服务 |
| **API文档** | http://localhost:8000/docs | Swagger UI |
| **健康检查** | http://localhost:8000/api/health/health | 服务状态 |

---

## 🔑 开发环境凭据

### API 认证
```
API Key: demo-test-key-12345
```

### 用户登录
```
管理员: admin / admin123
分析师: demo / demo123
```

---

## 📁 开发模式特点

### 热重载
- ✅ **前端**：Vite 自动热重载
- ✅ **后端**：`--reload` 模式，代码修改自动重启

### 挂载目录
```
./app      → /app/app       # 后端代码
./frontend → /app           # 前端代码
./data     → /app/data      # 数据库文件
./logs     → /app/logs      # 日志文件
```

### 数据库
- **类型**：SQLite
- **位置**：`./data/payguard_dev.db`
- **特点**：无需额外安装，数据持久化

---

## 🛠️ 常用命令

### 容器管理
```bash
# 查看运行状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志（所有服务）
docker-compose -f docker-compose.dev.yml logs -f

# 查看后端日志
docker-compose -f docker-compose.dev.yml logs -f backend

# 查看前端日志
docker-compose -f docker-compose.dev.yml logs -f frontend-dev

# 重启服务
docker-compose -f docker-compose.dev.yml restart

# 停止服务
docker-compose -f docker-compose.dev.yml down

# 完全清理（包括数据卷）
docker-compose -f docker-compose.dev.yml down -v
```

### 进入容器
```bash
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.dev.yml exec frontend-dev sh
```

### 测试 API
```bash
# 健康检查
curl http://localhost:8000/api/health/health

# 测试审计接口
curl -X POST http://localhost:8000/api/audit/transaction \
  -H "x-api-key: demo-test-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST001",
    "user_id": "USER001",
    "merchant_id": "MERCHANT001",
    "amount": 1000,
    "currency": "USD",
    "account_age_days": 100,
    "transaction_frequency_1h": 2,
    "ip_location_status": "normal",
    "device_status": "normal",
    "kyc_status": "verified",
    "merchant_risk_level": "low",
    "is_blacklisted": false,
    "timestamp": "2026-07-09T10:00:00"
  }'
```

---

## 🐛 故障排查

### 端口被占用
```bash
# Windows - 查看端口占用
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 杀死占用进程
taskkill /PID <进程ID> /F
```

### 容器无法启动
```bash
# 查看详细日志
docker-compose -f docker-compose.dev.yml logs

# 重新构建
docker-compose -f docker-compose.dev.yml build --no-cache

# 清理并重启
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### 前端依赖问题
```bash
# 进入前端容器重新安装
docker-compose -f docker-compose.dev.yml exec frontend-dev sh
npm install
```

### 数据库问题
```bash
# 删除数据库文件重新初始化
rm -f data/payguard_dev.db
docker-compose -f docker-compose.dev.yml restart backend
```

---

## 📊 开发环境配置

### 环境变量 (.env)
```bash
APP_ENV=development          # 开发环境
DEBUG=true                   # 启用调试模式
LOG_LEVEL=DEBUG              # 详细日志
DATABASE_TYPE=sqlite         # 使用 SQLite
LLM_PROVIDER=disabled        # 默认禁用 AI（节省成本）
```

### 修改配置
```bash
# 编辑环境变量
notepad .env

# 重启服务使配置生效
docker-compose -f docker-compose.dev.yml restart
```

---

## 🎯 开发工作流

### 1. 启动开发环境
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 2. 修改代码
- **后端**：编辑 `app/` 目录，自动重启
- **前端**：编辑 `frontend/src/`，热重载

### 3. 查看日志
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

### 4. 测试功能
- 访问 http://localhost:3000
- 使用 API 文档测试：http://localhost:8000/docs

### 5. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
```

---

## 📖 相关文档

- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) - 环境配置详解
- [README.md](README.md) - 项目总览
- [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) - 功能完善报告

---

## 💡 开发提示

### VS Code 集成
1. 安装 Docker 扩展
2. 右键容器 → Attach Shell
3. 可以直接在容器内调试

### 调试后端
```bash
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 运行 pytest
pytest tests/ -v

# 手动启动服务（用于调试）
uvicorn app.main:app --reload --host 0.0.0.0
```

### 调试前端
```bash
# 进入前端容器
docker-compose -f docker-compose.dev.yml exec frontend-dev sh

# 查看 npm 日志
npm run dev -- --debug
```

---

**当前状态：镜像正在构建中，请稍候...**

构建完成后，执行以下命令启动服务：
```bash
docker-compose -f docker-compose.dev.yml up -d
```

---

生成时间：2026-07-09
