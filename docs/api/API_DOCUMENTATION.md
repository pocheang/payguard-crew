# PayGuard API 完整文档

## 📋 目录

- [概述](#概述)
- [认证](#认证)
- [审计API](#审计api)
- [审核工作流API](#审核工作流api)
- [规则管理API](#规则管理api)
- [批量操作API](#批量操作api)
- [统计分析API](#统计分析api)
- [WebSocket API](#websocket-api)
- [错误处理](#错误处理)
- [限流说明](#限流说明)

---

## 概述

**Base URL**: `http://localhost:8000/api`

**版本**: v0.3.0

**协议**: HTTP/HTTPS

**数据格式**: JSON

---

## 认证

所有API请求需要在Header中提供API Key：

```http
X-API-Key: your-api-key-here
```

**获取API Key**: 联系系统管理员

---

## 审计API

### 1. 提交单笔交易审计

**POST** `/audit/transaction`

**限流**: 20次/分钟

**请求体**:
```json
{
  "transaction_id": "tx_20240101_001",
  "user_id": "user_123",
  "merchant_id": "merchant_456",
  "amount": 15000.00,
  "currency": "CNY",
  "timestamp": "2024-01-01T10:30:00Z",
  "location": {
    "country": "CN",
    "city": "Beijing",
    "ip": "192.168.1.1"
  },
  "device_info": {
    "device_id": "device_789",
    "device_type": "mobile"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "tx_20240101_001",
    "risk_score": 75,
    "risk_level": "high",
    "decision": "review",
    "triggered_rules": [
      {
        "rule_name": "large_amount",
        "weight": 8,
        "message": "交易金额超过阈值"
      }
    ],
    "ai_analysis": {
      "summary": "该交易存在多个风险信号...",
      "recommendation": "建议人工审核"
    }
  }
}
```

### 2. 查询审计报告

**GET** `/audit/report/{transaction_id}`

**限流**: 100次/分钟

**响应**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "tx_20240101_001",
    "risk_score": 75,
    "risk_level": "high",
    "decision": "review",
    "created_at": "2024-01-01T10:30:00Z"
  }
}
```

---

## 审核工作流API

### 1. 创建审核记录

**POST** `/review/create`

**请求体**:
```json
{
  "transaction_id": "tx_20240101_001",
  "priority": "high",
  "assigned_to": "reviewer_01"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "tx_20240101_001",
    "status": "pending",
    "priority": "high",
    "assigned_to": "reviewer_01",
    "created_at": "2024-01-01T10:31:00Z"
  }
}
```

### 2. 获取待审核列表

**GET** `/review/list/pending`

**参数**:
- `assigned_to` (可选): 审核员ID
- `priority` (可选): 优先级
- `limit` (默认100): 返回数量

**响应**:
```json
{
  "success": true,
  "total": 25,
  "data": [
    {
      "transaction_id": "tx_001",
      "status": "pending",
      "priority": "high",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 3. 更新审核状态

**POST** `/review/{transaction_id}/status`

**请求体**:
```json
{
  "status": "approved",
  "reviewer": "reviewer_01",
  "comment": "审核通过，风险可控"
}
```

### 4. 获取超时审核列表

**GET** `/review/list/overdue?timeout_hours=24`

### 5. 获取审核历史

**GET** `/review/{transaction_id}/history`

**响应**:
```json
{
  "success": true,
  "data": {
    "record": {...},
    "history": [
      {
        "user_id": "reviewer_01",
        "action": "approved",
        "comment": "审核通过",
        "created_at": "2024-01-01T11:00:00Z",
        "time_since_last": "30分钟"
      }
    ],
    "total_actions": 3
  }
}
```

### 6. 获取审核统计

**GET** `/review/statistics`

**响应**:
```json
{
  "success": true,
  "data": {
    "status_distribution": {
      "pending": 25,
      "in_review": 10,
      "approved": 150,
      "rejected": 30
    },
    "top_reviewers": [
      {
        "reviewer": "reviewer_01",
        "total_reviews": 150,
        "approved": 120,
        "rejected": 30,
        "approval_rate": 80.0,
        "avg_review_time_hours": 2.5
      }
    ],
    "overdue_reviews": 3,
    "today": {
      "total": 25,
      "approved": 20,
      "rejected": 5,
      "approval_rate": 80.0
    }
  }
}
```

---

## 规则管理API

### 1. 创建规则

**POST** `/rules`

**请求体**:
```json
{
  "name": "大额交易规则",
  "description": "交易金额超过10万元触发",
  "rule_type": "amount",
  "weight": 8,
  "condition": {
    "threshold": 100000,
    "operator": ">"
  },
  "action": {
    "risk_score": 30,
    "flag": "large_amount"
  }
}
```

### 2. 查询规则列表

**GET** `/rules?status=active&rule_type=amount`

### 3. 获取规则详情

**GET** `/rules/{rule_id}`

### 4. 更新规则

**PUT** `/rules/{rule_id}`

### 5. 激活/停用规则

**POST** `/rules/{rule_id}/activate`

**POST** `/rules/{rule_id}/deactivate`

### 6. 测试规则

**POST** `/rules/{rule_id}/test`

**请求体**:
```json
{
  "test_data": {
    "amount": 150000,
    "user_id": "user_123"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "rule_id": "rule_001",
    "rule_name": "大额交易规则",
    "matched": true,
    "message": "Amount 150000 > threshold 100000"
  }
}
```

### 7. 创建规则版本

**POST** `/rules/{rule_id}/versions`

### 8. 获取规则版本历史

**GET** `/rules/{rule_id}/versions`

### 9. 获取规则统计

**GET** `/rules/statistics/summary`

---

## 批量操作API

### 1. 批量审计

**POST** `/batch/audit`

**请求体**:
```json
{
  "transactions": [
    {...},
    {...}
  ]
}
```

### 2. 获取批量统计

**GET** `/batch/statistics`

---

## 统计分析API

### 1. 全局统计

**GET** `/statistics/global`

### 2. 时间序列数据

**GET** `/statistics/timeseries?hours=24`

### 3. TOP规则触发排行

**GET** `/statistics/top-rules?limit=10`

---

## WebSocket API

### 连接

**WS** `/ws?user_id=user123&token=xxx`

### 订阅房间

发送消息:
```json
{
  "type": "subscribe",
  "room": "reviews"
}
```

### 接收通知

```json
{
  "type": "review_assigned",
  "title": "新的审核任务",
  "data": {
    "transaction_id": "tx_001",
    "priority": "high"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**通知类型**:
- `review_assigned` - 审核任务分配
- `review_completed` - 审核完成
- `audit_completed` - 审计完成
- `system_alert` - 系统警告
- `data_updated` - 数据更新

---

## 错误处理

### 错误响应格式

```json
{
  "error": "Error Type",
  "detail": "详细错误信息",
  "status_code": 400
}
```

### 错误码

| 状态码 | 说明 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 限流说明

| API类型 | 限制 |
|--------|------|
| 审计接口 | 20次/分钟 |
| 查询接口 | 100次/分钟 |
| 批量接口 | 5次/分钟 |
| 默认 | 100次/分钟 |

**限流响应头**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1625097600
Retry-After: 30
```

---

## 最佳实践

### 1. 批量操作
使用批量API而非循环调用单个API

### 2. 缓存
相同查询在1分钟内会从缓存返回

### 3. WebSocket
用于实时通知，避免轮询

### 4. 错误重试
使用指数退避策略

---

**文档版本**: v0.3.0  
**更新日期**: 2026-07-10
