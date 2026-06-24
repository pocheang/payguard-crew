# PayGuard Crew API 文档

## 📖 API 概览

PayGuard Crew 提供基于 RESTful 的风控审计 API，支持交易风险评估、报告查询和日志追踪。

## 🔐 认证方式

所有 API 端点都需要 API Key 认证（开发模式除外）。

### 请求头格式
```http
X-API-Key: your-api-key-here
```

### 获取 API Key

生产环境：联系管理员获取 API Key

开发环境：在 `.env` 文件中配置 `API_KEYS`：
```bash
# 生成安全的 API Key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 在 .env 中配置（多个 Key 用逗号分隔）
API_KEYS=your-generated-key-1,your-generated-key-2
```

## 🚦 速率限制

为防止 API 滥用，系统实施以下速率限制：

- **每分钟**: 100 次请求
- **每小时**: 1000 次请求

超过限制将返回 `429 Too Many Requests`，响应头包含 `Retry-After` 字段。

## 📍 API 端点

### 1. 健康检查

#### 详细健康检查
```http
GET /health
```

**响应示例：**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-06-24T10:00:00Z",
  "environment": "dev",
  "components": {
    "database": {
      "status": "ok",
      "message": "SQLite connected",
      "latency_ms": 1.23
    },
    "knowledge_base": {
      "status": "ok",
      "message": "5 documents available"
    },
    "rag": {
      "status": "ok",
      "message": "Vector store initialized"
    },
    "llm": {
      "status": "ok",
      "message": "LLM disabled, using rule engine only"
    }
  }
}
```

#### 存活检查（Kubernetes Liveness）
```http
GET /health/live
```

#### 就绪检查（Kubernetes Readiness）
```http
GET /health/ready
```

---

### 2. 交易审计

#### 提交交易审核
```http
POST /audit/transaction
Content-Type: application/json
X-API-Key: your-api-key
```

**请求体：**
```json
{
  "transaction_id": "TX20260624001",
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
  "timestamp": "2026-06-24T10:30:00"
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transaction_id | string | 是 | 交易唯一标识 |
| user_id | string | 是 | 用户 ID |
| merchant_id | string | 是 | 商户 ID |
| amount | number | 是 | 交易金额 |
| currency | string | 是 | 货币代码（如 CNY, USD） |
| account_age_days | integer | 是 | 账户注册天数 |
| transaction_frequency_1h | integer | 是 | 近1小时交易次数 |
| ip_location_status | string | 是 | IP地址状态：normal/abnormal |
| device_status | string | 是 | 设备状态：normal/abnormal |
| kyc_status | string | 是 | KYC认证状态：verified/basic_verified/unverified |
| merchant_risk_level | string | 是 | 商户风险等级：low/medium/high |
| is_blacklisted | boolean | 是 | 是否在黑名单 |
| timestamp | string | 是 | 交易时间（ISO 8601） |

**响应示例：**
```json
{
  "transaction_id": "TX20260624001",
  "risk_level": "high",
  "risk_score": 95,
  "decision": "review",
  "summary": "交易触发多项高风险规则，包括新账户大额交易、高频交易、IP地址异常和设备异常，建议进行人工复核。",
  "triggered_rules": [
    {
      "rule_id": "R001",
      "rule_name": "new_account_high_amount",
      "reason": "账户注册小于7天且交易金额超过5000",
      "score": 25
    }
  ],
  "evidence": [
    {
      "source": "payment_risk_rules.md",
      "content": "## 新账户风险\n\n账户注册时间小于7天..."
    }
  ],
  "suggestion": "建议：1. 联系用户核实身份信息...",
  "requires_manual_review": true
}
```

**决策类型：**
- `approve` - 自动通过
- `review` - 需要人工复核
- `hold` - 暂扣交易
- `reject` - 直接拒绝

**风险等级：**
- `low` - 低风险（评分 < 30）
- `medium` - 中风险（评分 30-69）
- `high` - 高风险（评分 >= 70）

---

#### 查询审核报告
```http
GET /audit/report/{transaction_id}
X-API-Key: your-api-key
```

**响应示例：**
```json
{
  "transaction_id": "TX20260624001",
  "user_id": "U10086",
  "merchant_id": "M2033",
  "risk_score": 95,
  "risk_level": "high",
  "decision": "review",
  "summary": "交易触发多项高风险规则...",
  "suggestion": "建议：1. 联系用户核实身份信息...",
  "requires_manual_review": true,
  "created_at": "2026-06-24T10:35:22.123456+00:00",
  "triggered_rules": [...]
}
```

---

#### 查询审计日志
```http
GET /audit/logs/{transaction_id}
X-API-Key: your-api-key
```

**响应示例：**
```json
{
  "transaction_id": "TX20260624001",
  "logs": [
    {
      "agent_name": "transaction_agent",
      "input_data": "{...}",
      "output_data": "{...}",
      "status": "completed",
      "error_message": null,
      "latency_ms": 45,
      "created_at": "2026-06-24T10:35:21.001234+00:00"
    }
  ]
}
```

---

### 3. 监控指标

#### Prometheus Metrics
```http
GET /metrics
```

**指标列表：**

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| payguard_audit_requests_total | Counter | 审计请求总数 |
| payguard_audit_request_duration_seconds | Histogram | 审计请求耗时 |
| payguard_triggered_rules_total | Counter | 触发规则总数 |
| payguard_llm_requests_total | Counter | LLM 请求总数 |
| payguard_rag_retrieval_total | Counter | RAG 检索总数 |
| payguard_database_connections | Gauge | 数据库连接数 |

**Prometheus 配置示例：**
```yaml
scrape_configs:
  - job_name: 'payguard-crew'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

---

## 🔧 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | 未授权（缺少或无效的 API Key） |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 429 | 速率限制超出 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "error": "错误类型",
  "detail": "详细错误信息",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/audit/transaction"
}
```

---

## 📊 使用示例

### cURL 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 提交审核（使用 API Key）
curl -X POST http://localhost:8000/audit/transaction \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "transaction_id": "TX001",
    "user_id": "U001",
    "merchant_id": "M001",
    "amount": 1000,
    "currency": "CNY",
    "account_age_days": 10,
    "transaction_frequency_1h": 2,
    "ip_location_status": "normal",
    "device_status": "normal",
    "kyc_status": "verified",
    "merchant_risk_level": "low",
    "is_blacklisted": false,
    "timestamp": "2026-06-24T10:30:00"
  }'

# 查询报告
curl http://localhost:8000/audit/report/TX001 \
  -H "X-API-Key: your-api-key"
```

### Python 示例

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# 提交审核
transaction = {
    "transaction_id": "TX001",
    "user_id": "U001",
    "merchant_id": "M001",
    "amount": 1000,
    "currency": "CNY",
    "account_age_days": 10,
    "transaction_frequency_1h": 2,
    "ip_location_status": "normal",
    "device_status": "normal",
    "kyc_status": "verified",
    "merchant_risk_level": "low",
    "is_blacklisted": False,
    "timestamp": "2026-06-24T10:30:00"
}

response = requests.post(
    f"{API_URL}/audit/transaction",
    json=transaction,
    headers=headers
)

result = response.json()
print(f"风险等级: {result['risk_level']}")
print(f"决策: {result['decision']}")
```

### JavaScript/TypeScript 示例

```typescript
const API_URL = 'http://localhost:8000';
const API_KEY = 'your-api-key';

async function auditTransaction(transaction: any) {
  const response = await fetch(`${API_URL}/audit/transaction`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify(transaction),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// 使用
const result = await auditTransaction({
  transaction_id: 'TX001',
  user_id: 'U001',
  // ... 其他字段
});
```

---

## 🔍 请求追踪

每个请求都会返回唯一的 `X-Request-ID` 响应头，用于日志关联和问题排查。

客户端也可以主动提供 Request ID：
```http
X-Request-ID: your-custom-request-id
```

---

## 🛡️ 安全最佳实践

1. **保护 API Key**：不要在代码中硬编码，使用环境变量
2. **使用 HTTPS**：生产环境必须使用 TLS 加密
3. **实施速率限制**：按需调整限流参数
4. **监控异常请求**：通过 Prometheus 监控指标
5. **日志审计**：定期审查访问日志

---

## 📚 相关文档

- [README.md](../README.md) - 项目概览
- [USAGE_GUIDE.md](../USAGE_GUIDE.md) - 使用指南
- [风控规则说明](../README.md#风控规则说明) - 规则详情

---

**版本**: v0.1.0  
**最后更新**: 2026-06-24
