# PayGuard Crew - Demo 演示指南

## 快速开始

### 1. 启动服务器

```bash
cd c:\Users\pocheang\Downloads\payguard_crew_starter\payguard_crew_starter
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. 运行自动化Demo脚本

```bash
# 安装依赖
pip install requests

# 运行demo
python scripts/demo_test.py
```

---

## 手动测试步骤

### 准备工作

```bash
# 设置变量
export BASE_URL="http://127.0.0.1:8000"
export API_KEY="demo-test-key-12345"
```

Windows PowerShell:
```powershell
$BASE_URL = "http://127.0.0.1:8000"
$API_KEY = "demo-test-key-12345"
```

---

## 测试场景

### 场景1: 健康检查

```bash
curl http://127.0.0.1:8000/api/health/health
```

**预期结果**:
```json
{
  "status": "degraded",
  "version": "0.1.1",
  "components": {
    "database": {"status": "ok"},
    "knowledge_base": {"status": "ok"}
  }
}
```

---

### 场景2: 正常交易审计

**测试数据**: 美国国内小额转账（低风险）

```bash
curl -X POST "http://127.0.0.1:8000/api/audit/transaction" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "TXN_NORMAL_001",
    "amount": 1000.00,
    "currency": "USD",
    "sender": {
      "user_id": "user_alice",
      "account": "alice@example.com",
      "country": "US"
    },
    "receiver": {
      "user_id": "user_bob",
      "account": "bob@example.com",
      "country": "US"
    }
  }'
```

**预期**: 风险等级 LOW，通过审计

---

### 场景3: 高风险交易

**测试数据**: 大额跨境转账（高风险）

```bash
curl -X POST "http://127.0.0.1:8000/api/audit/transaction" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "TXN_HIGH_RISK_001",
    "amount": 50000.00,
    "currency": "USD",
    "sender": {
      "user_id": "user_charlie",
      "account": "charlie@example.com",
      "country": "NG",
      "ip": "41.203.72.1"
    },
    "receiver": {
      "user_id": "user_david",
      "account": "david@example.com",
      "country": "CN",
      "ip": "220.181.38.148"
    }
  }'
```

**预期**: 风险等级 HIGH，触发多个规则：
- 大额交易规则
- 高风险国家规则
- 跨境交易规则

---

### 场景4: 可疑交易

**测试数据**: 临时邮箱 + 制裁国家（极高风险）

```bash
curl -X POST "http://127.0.0.1:8000/api/audit/transaction" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "TXN_SUSPICIOUS_001",
    "amount": 9999.00,
    "currency": "USD",
    "sender": {
      "user_id": "user_eve",
      "account": "eve@tempmail.com",
      "country": "RU"
    },
    "receiver": {
      "user_id": "user_mallory",
      "account": "mallory@anonymail.org",
      "country": "KP"
    }
  }'
```

**预期**: 风险等级 CRITICAL，触发：
- 临时邮箱规则
- 制裁国家规则
- 整数金额规则

---

### 场景5: 批量交易审计

```bash
curl -X POST "http://127.0.0.1:8000/api/audit/batch" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "batch_id": "BATCH_DEMO_001",
    "transactions": [
      {
        "transaction_id": "TXN_001",
        "amount": 500,
        "currency": "USD",
        "sender": {"user_id": "u1", "account": "a1@test.com"},
        "receiver": {"user_id": "u2", "account": "a2@test.com"}
      },
      {
        "transaction_id": "TXN_002",
        "amount": 25000,
        "currency": "USD",
        "sender": {"user_id": "u3", "account": "a3@test.com", "country": "NG"},
        "receiver": {"user_id": "u4", "account": "a4@test.com", "country": "CN"}
      },
      {
        "transaction_id": "TXN_003",
        "amount": 9999,
        "currency": "USD",
        "sender": {"user_id": "u5", "account": "temp@tempmail.com"},
        "receiver": {"user_id": "u6", "account": "anon@anonymail.org"}
      }
    ]
  }'
```

**预期**: 返回批量审计结果和风险统计

---

### 场景6: 创建审核任务

```bash
curl -X POST "http://127.0.0.1:8000/api/review/create" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "TXN_HIGH_RISK_001",
    "reviewer": "reviewer_alice",
    "priority": "high",
    "notes": "Large cross-border transaction requires manual review"
  }'
```

**预期**: 创建审核任务，返回 review_id

---

### 场景7: 查询审计历史

```bash
curl "http://127.0.0.1:8000/api/audit/list?limit=10" \
  -H "x-api-key: demo-test-key-12345"
```

---

### 场景8: 导出审计报告

**CSV格式**:
```bash
curl "http://127.0.0.1:8000/api/audit/export/csv?start_date=2026-07-01&end_date=2026-07-31" \
  -H "x-api-key: demo-test-key-12345" \
  -o audit_report.csv
```

**Excel格式**:
```bash
curl "http://127.0.0.1:8000/api/audit/export/excel?start_date=2026-07-01" \
  -H "x-api-key: demo-test-key-12345" \
  -o audit_report.xlsx
```

---

## 测试数据说明

### 低风险交易特征
- ✅ 小额交易（< $10,000）
- ✅ 同国家/地区
- ✅ 正常邮箱域名
- ✅ 非制裁国家

### 高风险交易特征
- ⚠️ 大额交易（> $10,000）
- ⚠️ 跨境交易
- ⚠️ 高风险国家（NG, CN, RU等）
- ⚠️ 整数金额（反洗钱特征）

### 极高风险特征
- 🚫 临时邮箱域名
- 🚫 制裁国家（KP, IR, SY等）
- 🚫 匿名服务
- 🚫 多个高风险因素叠加

---

## 访问Web界面

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **API概览**: http://127.0.0.1:8000/

在Swagger UI中可以：
1. 查看所有API文档
2. 直接测试API（Try it out）
3. 查看请求/响应示例
4. 下载OpenAPI规范

---

## 演示要点

### 1. 展示风险识别能力
- 演示不同风险等级的交易
- 展示规则引擎如何匹配和评分
- 强调实时风险评估

### 2. 展示合规能力
- 制裁国家检测
- AML/KYC规则
- 监管要求覆盖

### 3. 展示审核工作流
- 高风险交易自动进入审核队列
- 审核员分配和追踪
- 审核历史记录

### 4. 展示批量处理
- 支持批量交易审计
- 实时统计和分析
- 导出功能

---

## 故障排查

### 问题1: 服务器未启动
```bash
# 检查是否运行
netstat -ano | findstr :8000

# 启动服务器
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 问题2: 认证失败
确认 API Key 正确:
```
demo-test-key-12345
```

### 问题3: 路由404
注意当前路由有双重前缀:
- `/api/auth/auth/login` (当前)
- `/api/health/health` (当前)

---

## 下一步

1. **修复路由前缀问题**
2. **升级 bcrypt 库**
3. **添加更多测试数据**
4. **配置生产环境**
