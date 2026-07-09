# API 规范化问题分析

## 🔍 发现的问题

### 1. **重复的审计API**
- ❌ `app/api/audit.py` - 基础版本
- ❌ `app/api/audit_secure.py` - 安全加固版本
- **问题**: 两个文件功能重复，endpoint相同，应该只保留一个

### 2. **路由前缀混乱**
```python
# batch.py
router = APIRouter(prefix="/api/v1/audit", tags=["batch-audit"])

# review.py  
router = APIRouter(prefix="/api/v1/review", tags=["review-workflow"])

# audit.py
router = APIRouter()  # 无前缀，在main.py中加前缀

# v1.py
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(audit_router, prefix="/audit")
```

**问题**: 
- batch和review在router中写死了 `/api/v1`
- audit在v1.py中才加前缀
- 导致同时存在 legacy 和 v1 两套路由

### 3. **main.py 中的重复注册**
```python
# 注册路由 - API v1 (推荐)
app.include_router(api_v1_router)  # 包含 /api/v1/audit/*
app.include_router(batch_router)   # 又注册了 /api/v1/audit/batch

# 注册路由 - Legacy (兼容)
app.include_router(legacy_router)  # 又包含 /audit/*
```

**问题**: batch和review被重复注册

## ✅ 建议的规范结构

### 方案A: 统一使用 v1 路由管理（推荐）

```
/api/v1/audit/transaction      # 提交审计
/api/v1/audit/report/{id}      # 查询报告
/api/v1/audit/logs/{id}        # 查询日志
/api/v1/audit/batch            # 批量审计
/api/v1/audit/export/csv       # 导出CSV
/api/v1/audit/export/excel     # 导出Excel
/api/v1/audit/statistics       # 统计信息

/api/v1/review/create          # 创建审核
/api/v1/review/{id}            # 审核详情
/api/v1/review/pending         # 待审核列表

/api/v1/auth/*                 # 认证
/api/v1/health                 # 健康检查
/api/v1/metrics                # 监控指标
```

### 方案B: 扁平化路由（更简单）

```
/api/audit/transaction         # 提交审计
/api/audit/batch              # 批量审计
/api/review/create            # 创建审核
/api/health                   # 健康检查
```

## 🛠️ 修复步骤

1. **删除 audit.py，重命名 audit_secure.py → audit.py**
2. **统一路由前缀管理**: 所有router不写死前缀，在v1.py统一管理
3. **修复main.py**: 避免重复注册
4. **清理legacy路由**: 决定是否保留向后兼容

## 📊 当前路由混乱示意

```
Current (混乱):
/audit/transaction           ← legacy_router (audit.py)
/api/v1/audit/transaction    ← api_v1_router (audit.py)
/api/v1/audit/batch          ← batch_router (直接注册)
/api/v1/audit/batch          ← 可能通过v1_router重复？

Should be (清晰):
/api/v1/audit/transaction
/api/v1/audit/batch
/api/v1/audit/export/csv
/api/v1/review/create
```
