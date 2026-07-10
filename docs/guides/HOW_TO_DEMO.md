# PayGuard Crew - Demo 完整说明

## 🎯 如何演示项目

### 方式1: 使用 Swagger UI（推荐）

**最简单的演示方式**

1. 启动服务器：
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

2. 打开浏览器访问：
```
http://127.0.0.1:8000/docs
```

3. 在Swagger UI中可以：
   - 查看所有API文档
   - 点击 "Try it out" 直接测试
   - 查看示例请求和响应
   - 不需要命令行

---

### 方式2: 自动化Demo脚本

```bash
# 安装依赖
pip install requests

# 运行demo
python scripts/demo_test.py
```

**当前状态**: 
- ✅ 健康检查 - 正常
- ⚠️ 登录功能 - bcrypt兼容性问题
- ⚠️ 交易审计 - 数据模型需要完整字段
- ✅ 审核工作流 - 正常

---

### 方式3: 手动测试（适合技术演示）

#### 测试1: 健康检查 ✅

```bash
curl http://127.0.0.1:8000/api/health/health
```

**结果**: 返回系统状态、版本、各组件健康度

---

#### 测试2: 查看交易数据模型

访问 Swagger UI 查看完整的数据模型要求：
http://127.0.0.1:8000/docs#/audit/audit_transaction_api_audit_transaction_post

**必需字段**:
```json
{
  "transaction_id": "string",
  "user_id": "string",
  "amount": 0,
  "currency": "string",
  "merchant_id": "string",
  "account_age_days": 0,
  "transaction_frequency_1h": 0,
  "ip_location_status": "matched",
  "device_status": "recognized",
  "kyc_status": "verified",
  "merchant_risk_level": "low",
  "timestamp": "2026-07-08T10:00:00Z"
}
```

---

#### 测试3: 完整交易审计示例

```bash
curl -X POST "http://127.0.0.1:8000/api/audit/transaction" \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-test-key-12345" \
  -d '{
    "transaction_id": "TXN_DEMO_001",
    "user_id": "user_alice",
    "amount": 1000.00,
    "currency": "USD",
    "merchant_id": "merchant_001",
    "account_age_days": 365,
    "transaction_frequency_1h": 1,
    "ip_location_status": "matched",
    "device_status": "recognized",
    "kyc_status": "verified",
    "merchant_risk_level": "low",
    "timestamp": "2026-07-08T10:00:00Z",
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

---

## 📊 演示数据已准备

### 数据库状态
- ✅ SQLite 数据库已创建: `payguard_crew.db`
- ✅ 表结构已初始化
- ✅ 知识库已加载 (9个文档)

### 默认凭证
```
API Key: demo-test-key-12345

用户: admin / admin123 (super_admin角色)
用户: demo / demo123 (analyst角色)
```

---

## 🎬 演示流程建议

### 场景1: 基础功能展示 (5分钟)

1. **启动服务** - 展示快速启动
2. **访问 Swagger UI** - 展示API文档
3. **健康检查** - 展示系统状态
4. **查看API列表** - 展示功能覆盖

### 场景2: 风险审计演示 (10分钟)

1. **正常交易** - 低风险，快速通过
2. **高风险交易** - 大额/跨境，触发规则
3. **可疑交易** - 多个风险因素，拦截
4. **查看审计日志** - 展示历史记录

### 场景3: 审核工作流 (5分钟)

1. **创建审核任务** - 高风险交易进入队列
2. **查询审核状态** - 展示工作流
3. **导出报告** - CSV/Excel格式

---

## 🔧 已知问题及解决方案

### 问题1: 路由双重前缀
**现象**: `/api/auth/auth/login` 而不是 `/api/auth/login`
**影响**: API路径不够简洁，但功能正常
**解决**: 在Swagger UI中可以正常使用

### 问题2: bcrypt密码哈希
**现象**: 登录时密码验证错误
**影响**: JWT认证功能受限
**解决**: 
```bash
pip install --upgrade bcrypt passlib
```

### 问题3: 交易审计需要完整字段
**现象**: 缺少必填字段会返回422错误
**影响**: 测试数据需要完整
**解决**: 使用Swagger UI中的示例数据

---

## 💡 Demo技巧

### 1. 使用Swagger UI进行演示
- **优点**: 可视化、交互式、无需命令行
- **操作**: 点击API → Try it out → 填写参数 → Execute
- **展示**: 实时看到请求/响应

### 2. 准备演示话术

**健康检查**:
> "系统提供了完整的健康检查端点，可以实时监控各个组件的状态，包括数据库、知识库、RAG系统等"

**风险审计**:
> "规则引擎可以实时评估交易风险，基于金额、国家、账户状态等多个维度进行综合评分"

**合规能力**:
> "系统内置了AML/KYC规则，支持制裁国家检测、临时邮箱识别等合规要求"

### 3. 重点展示

✅ **快速启动** - 一条命令启动完整系统
✅ **API文档** - 完整的Swagger文档
✅ **健康监控** - 实时系统状态
✅ **审核工作流** - 高风险交易人工审核
✅ **数据导出** - CSV/Excel报告

---

## 🎯 适合不同受众的演示重点

### 技术人员
- 展示代码结构和架构
- API设计和文档
- 可扩展性和性能

### 业务人员
- 风险识别能力
- 合规覆盖范围
- 审核工作流

### 管理层
- 快速部署能力
- 成本效益
- 扩展性和维护性

---

## 📁 相关文档

- [DEMO_STATUS.md](DEMO_STATUS.md) - 详细状态报告
- [DEMO_GUIDE.md](DEMO_GUIDE.md) - 完整测试指南
- [README.md](README.md) - 项目介绍
- Swagger UI: http://127.0.0.1:8000/docs

---

## 🚀 快速开始命令

```bash
# 1. 启动服务器
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 在浏览器中打开
start http://127.0.0.1:8000/docs

# 3. 或者使用健康检查测试
curl http://127.0.0.1:8000/api/health/health
```

---

## ✅ Demo就绪清单

- [x] 服务器可以启动
- [x] Swagger UI可以访问
- [x] 健康检查正常
- [x] 数据库已初始化
- [x] API文档完整
- [x] 测试数据准备
- [x] 演示脚本可用
- [ ] 修复路由前缀（可选）
- [ ] 升级bcrypt（可选）

**结论**: 项目已经可以进行Demo演示！

建议使用Swagger UI进行可视化演示，这是最直观、最容易理解的方式。
