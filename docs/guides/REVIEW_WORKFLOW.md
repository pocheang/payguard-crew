# 审核工作流使用指南

**新增功能**: v0.2.0  
**适用场景**: 团队协作、人工审核、合规管理

---

## 🎯 功能概述

审核工作流提供完整的人工审核流程管理，适合高风险交易的二次审核场景。

### 核心功能

- ✅ **状态流转**: 6种状态，清晰的流转规则
- ✅ **任务分配**: 灵活的审核人分配
- ✅ **评论协作**: 团队协作讨论
- ✅ **优先级**: 4级优先级管理
- ✅ **审核历史**: 完整的操作记录
- ✅ **统计分析**: 审核效率分析

---

## 📊 状态机设计

### 6种审核状态

| 状态 | 说明 | 可流转到 |
|------|------|----------|
| **PENDING** | 待审核 | IN_REVIEW, ARCHIVED |
| **IN_REVIEW** | 审核中 | APPROVED, REJECTED, ESCALATED |
| **APPROVED** | 已批准 | ARCHIVED |
| **REJECTED** | 已拒绝 | ARCHIVED, IN_REVIEW |
| **ESCALATED** | 已升级 | IN_REVIEW, ARCHIVED |
| **ARCHIVED** | 已归档 | 不可流转 |

---

## 🚀 7个新API接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/v1/review/create` | POST | 创建审核记录 |
| `/api/v1/review/{tx_id}/status` | POST | 更新审核状态 |
| `/api/v1/review/{tx_id}/assign` | POST | 分配审核人 |
| `/api/v1/review/{tx_id}/comment` | POST | 添加评论 |
| `/api/v1/review/{tx_id}` | GET | 获取审核详情 |
| `/api/v1/review/pending` | GET | 待审核列表 |
| `/api/v1/review/statistics` | GET | 审核统计 |

---

## 💼 完整使用流程

### 1. 创建审核记录

```bash
curl -X POST "http://localhost:8000/api/v1/review/create" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TX001",
    "priority": "high",
    "assigned_to": "reviewer01"
  }'
```

### 2. 开始审核

```bash
curl -X POST "http://localhost:8000/api/v1/review/TX001/status" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "status": "in_review",
    "reviewer": "reviewer01",
    "comment": "开始审核"
  }'
```

### 3. 批准/拒绝

```bash
# 批准
curl -X POST "http://localhost:8000/api/v1/review/TX001/status" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "status": "approved",
    "reviewer": "reviewer01",
    "comment": "已核实，批准通过"
  }'
```

### 4. 查看待办

```bash
# 我的待审核
curl -X GET "http://localhost:8000/api/v1/review/pending?assigned_to=reviewer01" \
  -H "X-API-Key: YOUR_API_KEY"

# 高优先级
curl -X GET "http://localhost:8000/api/v1/review/pending?priority=high" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 📁 新增文件

1. `app/db/schemas_review.py` - 数据库Schema
2. `app/services/review_service.py` - 工作流服务
3. `app/api/review.py` - API接口
4. `REVIEW_WORKFLOW.md` - 本文档

---

## ✅ 功能清单

- [x] 创建审核记录
- [x] 6种状态流转
- [x] 分配审核人
- [x] 添加评论
- [x] 查看详情和历史
- [x] 待办列表查询
- [x] 统计分析
- [x] 4级优先级

**状态**: ✅ 功能完整，可立即使用

详细文档请访问: http://localhost:8000/docs
