# 🚀 快速开始指南 (Quick Start Guide)

## 🎯 5分钟快速启动

### 1. 安装依赖
```bash
# 克隆项目
git clone https://github.com/pocheang/payguard-crew
cd payguard-crew

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境
```bash
# 创建 .env 文件（开发环境）
cat > .env << EOF
APP_ENV=dev
DATABASE_TYPE=sqlite
LLM_PROVIDER=disabled
ENABLE_CREWAI=false
OTEL_ENABLED=false
JWT_SECRET_KEY=dev-secret-change-in-production
EOF
```

### 3. 启动服务
```bash
uvicorn app.main:app --reload
```

### 4. 访问API文档
打开浏览器访问: http://localhost:8000/docs

---

## 🔐 测试认证功能

### 登录获取Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**默认用户:**
- `admin` / `admin123` (超级管理员)
- `demo` / `demo123` (分析师)

### 使用Token访问API
```bash
# 保存上一步返回的 access_token
TOKEN="YOUR_ACCESS_TOKEN"

# 访问受保护的端点
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 💳 测试交易风控

### 1. 审计交易 (无需认证)
```bash
curl -X POST http://localhost:8000/audit/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TX20260625001",
    "user_id": "U10086",
    "merchant_id": "M2033",
    "amount": 9800,
    "currency": "CNY",
    "account_age_days": 3,
    "transaction_frequency_1h": 12,
    "ip_location_status": "abnormal",
    "device_status": "abnormal",
    "kyc_status": "basic_verified",
    "merchant_risk_level": "medium",
    "is_blacklisted": false,
    "timestamp": "2026-06-25T10:30:00"
  }'
```

### 2. 查看审计报告
```bash
curl http://localhost:8000/audit/report/TX20260625001
```

### 3. 查看执行日志
```bash
curl http://localhost:8000/audit/logs/TX20260625001
```

---

## 🏗️ 项目结构

```
payguard_crew_starter/
├── app/
│   ├── api/              # API路由
│   │   ├── audit.py      # 交易审计
│   │   ├── auth.py       # 🆕 JWT认证
│   │   ├── health.py     # 健康检查
│   │   └── v1.py         # 🆕 API版本管理
│   ├── core/             # 🆕 核心企业功能
│   │   ├── auth.py       # JWT & RBAC
│   │   ├── logging.py    # 结构化日志
│   │   ├── tracing.py    # 分布式追踪
│   │   └── monitoring.py # 错误追踪
│   ├── db/               # 数据库
│   │   ├── database.py   # SQLite连接
│   │   └── database_engine.py  # 🆕 生产数据库引擎
│   ├── rules/            # 风控规则引擎
│   ├── schemas/          # 数据模型
│   └── main.py           # FastAPI应用入口
├── k8s/                  # 🆕 Kubernetes部署
├── .github/workflows/    # 🆕 CI/CD流水线
├── docs/                 # 知识库文档
├── tests/                # 测试套件
├── requirements.txt      # 基础依赖
├── requirements-prod.txt # 🆕 生产依赖
└── .env.production.template  # 🆕 生产配置模板
```

---

## 📊 系统架构对比

### 原版 (Demo)
```
用户 → FastAPI → SQLite → 规则引擎
```

### 企业版 (v0.2.0)
```
用户 → 负载均衡 → Kubernetes (3-10个Pod)
                      ↓
        JWT认证 + RBAC权限控制
                      ↓
              规则引擎 + AI Agents
                      ↓
    PostgreSQL + ChromaDB + Redis
                      ↓
        监控: Prometheus + Grafana
        日志: ELK / Datadog
        追踪: Jaeger / Tempo
        错误: Sentry
```

---

## 🎓 核心功能特性

### ✅ 原有功能
- 7大类风控规则 (R001-R007)
- 风险评分计算 (0-100)
- Multi-Agent协作 (CrewAI)
- RAG知识库检索 (ChromaDB)
- 合规审计 (KYC/AML)

### 🆕 企业级新功能
- **JWT认证** - Token-based身份验证
- **RBAC权限** - 9个角色，26种权限
- **生产数据库** - PostgreSQL/MySQL支持
- **连接池** - 20基础 + 40溢出连接
- **结构化日志** - JSON格式，带关联ID
- **分布式追踪** - OpenTelemetry集成
- **错误追踪** - Sentry集成
- **自动扩容** - Kubernetes HPA (3-10 pods)
- **CI/CD流水线** - GitHub Actions
- **安全扫描** - Bandit + Safety + Trivy

---

## 🔧 开发模式 vs 生产模式

### 开发模式
```bash
# .env
APP_ENV=dev
DATABASE_TYPE=sqlite
LLM_PROVIDER=disabled
OTEL_ENABLED=false

# 启动
uvicorn app.main:app --reload
```

### 生产模式
```bash
# .env.production
APP_ENV=production
DATABASE_TYPE=postgresql
POSTGRES_PASSWORD=secure_password
JWT_SECRET_KEY=<secure-random-key>
OTEL_ENABLED=true
SENTRY_DSN=https://...

# 部署到Kubernetes
kubectl apply -f k8s/production/
```

---

## 📚 文档导航

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目总览和功能介绍 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 生产部署完整指南 |
| [ENTERPRISE_ARCHITECTURE.md](ENTERPRISE_ARCHITECTURE.md) | 架构设计文档 |
| [SECURITY_SECTION.md](SECURITY_SECTION.md) | 安全实施指南 |
| [ENTERPRISE_FEATURES.md](ENTERPRISE_FEATURES.md) | 企业功能总结 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 🆕 常见问题解决 |

---

## 🐛 遇到问题？

### 常见错误解决

1. **导入错误**: 检查是否安装所有依赖
```bash
pip install -r requirements.txt
```

2. **数据库错误**: 确认DATABASE_TYPE配置
```bash
# 开发用SQLite
DATABASE_TYPE=sqlite
```

3. **认证错误**: 生成新的JWT密钥
```bash
openssl rand -hex 32
```

详细解决方案请查看: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🚀 下一步

### 学习路径
1. ✅ 完成快速启动
2. 📖 阅读 [ENTERPRISE_FEATURES.md](ENTERPRISE_FEATURES.md) 了解新功能
3. 🔐 学习 [SECURITY_SECTION.md](SECURITY_SECTION.md) 了解安全措施
4. 🏗️ 阅读 [DEPLOYMENT.md](DEPLOYMENT.md) 准备生产部署
5. 🧪 运行测试套件: `pytest tests/ -v`

### 生产部署
1. 设置PostgreSQL数据库
2. 配置 `.env.production`
3. 生成安全密钥
4. 部署到Kubernetes
5. 配置监控和告警

---

## 📞 获取帮助

- **GitHub Issues**: 报告bug或功能请求
- **文档**: 查看完整的部署和架构文档
- **示例**: 参考 `data/sample_transaction.json`

---

**版本**: v0.2.0 (企业版)  
**最后更新**: 2026-06-25  
**状态**: ✅ 生产就绪
