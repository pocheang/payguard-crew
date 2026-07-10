# 项目代码组织指南

> **目标**: 保持代码清晰、模块化、易于扩展  
> **原则**: 单一职责、高内聚低耦合、可测试

---

## 📁 项目结构规范

### 推荐的目录结构

```
payguard_crew_starter/
├── app/                      # 后端应用
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   │
│   ├── api/                 # API路由层
│   │   ├── __init__.py
│   │   ├── audit.py         # 审计接口
│   │   ├── review.py        # 审核接口
│   │   ├── auth.py          # 认证接口
│   │   └── dependencies.py  # 依赖注入
│   │
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── environment.py   # 环境配置
│   │   ├── cache.py         # 缓存管理
│   │   ├── logging.py       # 日志配置
│   │   └── metrics.py       # 性能指标
│   │
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── review_service.py
│   │   ├── rule_service.py
│   │   └── audit_service.py
│   │
│   ├── db/                  # 数据访问层
│   │   ├── __init__.py
│   │   ├── database.py      # 连接管理
│   │   ├── models.py        # 数据模型
│   │   ├── repositories.py  # 数据仓库
│   │   └── migrations/      # 数据库迁移
│   │
│   ├── auth/                # 认证授权
│   │   ├── __init__.py
│   │   ├── api_key.py
│   │   └── jwt.py
│   │
│   ├── security/            # 安全模块
│   │   ├── __init__.py
│   │   └── validators.py
│   │
│   ├── rules/               # 规则引擎
│   │   ├── __init__.py
│   │   └── engine.py
│   │
│   ├── utils/               # 工具函数
│   │   ├── __init__.py
│   │   ├── datetime_utils.py
│   │   └── response.py
│   │
│   └── schemas/             # Pydantic模型
│       ├── __init__.py
│       ├── transaction.py
│       └── audit.py
│
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # Vue组件
│   │   │   ├── common/     # 通用组件
│   │   │   ├── charts/     # 图表组件
│   │   │   └── forms/      # 表单组件
│   │   ├── composables/    # 组合式函数
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── services/       # 服务层
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   ├── App.vue
│   │   └── main.js
│   │
│   ├── public/             # 公共资源
│   ├── package.json
│   └── vite.config.js
│
├── tests/                   # 测试
│   ├── __init__.py
│   ├── conftest.py         # Pytest配置
│   ├── api/                # API测试
│   ├── services/           # 服务测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
│
├── docs/                    # 文档
│   ├── reports/            # 审查报告
│   ├── guides/             # 使用指南
│   ├── api/                # API文档
│   └── architecture/       # 架构文档
│
├── scripts/                 # 脚本工具
│   ├── deploy.sh
│   ├── verify-fixes.sh
│   └── setup.sh
│
├── .env.example            # 环境变量示例
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md               # 主文档
```

---

## 📋 文档组织规范

### 文档分类

```
docs/
├── reports/                 # 技术报告
│   ├── CODE_REVIEW_REPORT.md
│   ├── PERFORMANCE_OPTIMIZATION_REPORT.md
│   └── SECURITY_AUDIT_REPORT.md
│
├── guides/                  # 使用指南
│   ├── QUICK_START.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── API_GUIDE.md
│
├── architecture/            # 架构文档
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   └── FRONTEND_ARCHITECTURE.md
│
└── README.md               # 文档索引
```

**根目录只保留**:
- `README.md` - 主文档（项目介绍）
- `CHANGELOG.md` - 版本变更
- `CONTRIBUTING.md` - 贡献指南（可选）
- `LICENSE` - 许可证

---

## 🎯 代码组织原则

### 1. 模块职责清晰

```python
# ✅ 好的实践：单一职责
# app/services/audit_service.py
def audit_transaction(tx: Transaction) -> AuditResult:
    """审计交易 - 只负责业务逻辑"""
    pass

# app/db/repositories.py
def save_audit_result(result: AuditResult) -> None:
    """保存结果 - 只负责数据访问"""
    pass

# app/api/audit.py
@router.post("/audit")
def audit_endpoint(tx: Transaction):
    """API接口 - 只负责HTTP处理"""
    result = audit_transaction(tx)
    save_audit_result(result)
    return result
```

```python
# ❌ 不好的实践：职责混乱
@router.post("/audit")
def audit_endpoint(tx: Transaction):
    # 混合了业务逻辑、数据访问、HTTP处理
    score = calculate_risk(tx)  # 业务逻辑
    conn = sqlite3.connect()    # 数据访问
    conn.execute("INSERT ...")   # 数据访问
    return {"score": score}      # HTTP响应
```

### 2. 依赖注入

```python
# ✅ 使用依赖注入
from app.db.database import get_db

@router.get("/audits")
def list_audits(db: Connection = Depends(get_db)):
    return fetch_audits(db)
```

### 3. 类型提示

```python
# ✅ 完整的类型提示
from typing import List, Optional

def get_reviews(
    assigned_to: Optional[str] = None,
    limit: int = 100
) -> List[dict]:
    """获取审核列表"""
    pass
```

### 4. 文档字符串

```python
# ✅ 清晰的文档
def audit_transaction(tx: Transaction) -> AuditResult:
    """
    审计交易

    Args:
        tx: 交易数据

    Returns:
        审计结果，包含风险分数和决策

    Raises:
        ValueError: 交易数据无效
    """
    pass
```

---

## 🔧 前端组织规范

### 组件分类

```
components/
├── common/              # 通用组件（可复用）
│   ├── Button.vue
│   ├── Input.vue
│   ├── Modal.vue
│   └── Card.vue
│
├── charts/              # 图表组件
│   ├── RiskTrendChart.vue
│   └── PieChart.vue
│
├── forms/               # 表单组件
│   ├── TransactionForm.vue
│   └── ReviewForm.vue
│
└── business/            # 业务组件（特定功能）
    ├── RiskIndicator.vue
    └── ReviewStatus.vue
```

### 组件命名规范

```javascript
// ✅ 多词组件名
export default {
  name: 'RiskTrendChart'  // 好
}

// ❌ 单词组件名
export default {
  name: 'Chart'  // 避免
}
```

### Composables组织

```javascript
// composables/useAudit.js
export function useAudit() {
  const loading = ref(false)
  const error = ref(null)

  async function auditTransaction(tx) {
    loading.value = true
    try {
      const result = await api.audit(tx)
      return result
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  return { loading, error, auditTransaction }
}
```

---

## 📦 模块导入规范

### Python导入顺序

```python
# 1. 标准库
import os
from pathlib import Path

# 2. 第三方库
from fastapi import FastAPI
from pydantic import BaseModel

# 3. 本地模块
from app.config import get_settings
from app.db.database import get_connection
from app.services.audit import audit_transaction
```

### JavaScript导入顺序

```javascript
// 1. Vue核心
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

// 2. 第三方库
import axios from 'axios'

// 3. 本地模块
import api from '@/services/api'
import { useAudit } from '@/composables/useAudit'
```

---

## 🧪 测试组织

### 测试文件对应

```
app/services/audit_service.py
→ tests/services/test_audit_service.py

app/api/audit.py
→ tests/api/test_audit.py
```

### 测试命名

```python
# ✅ 描述性测试名
def test_audit_transaction_with_valid_data():
    pass

def test_audit_transaction_raises_error_with_invalid_amount():
    pass

# ❌ 模糊的测试名
def test_audit():
    pass
```

---

## 🗂️ 配置文件组织

```
.
├── .env.example          # 配置说明
├── .env.development      # 开发配置
├── .env.production       # 生产配置
├── pytest.ini            # Pytest配置
├── .eslintrc.js          # ESLint配置
├── .prettierrc           # Prettier配置
└── docker-compose.yml    # Docker编排
```

---

## 🚀 扩展指南

### 添加新API接口

1. **创建路由** (`app/api/new_feature.py`)
```python
from fastapi import APIRouter

router = APIRouter(tags=["new-feature"])

@router.post("/new")
def new_endpoint():
    pass
```

2. **注册路由** (`app/main.py`)
```python
from app.api.new_feature import router as new_router

app.include_router(new_router, prefix="/api/new")
```

3. **添加测试** (`tests/api/test_new_feature.py`)
```python
def test_new_endpoint():
    response = client.post("/api/new")
    assert response.status_code == 200
```

### 添加新服务

1. **创建服务** (`app/services/new_service.py`)
```python
def new_business_logic(data: dict) -> dict:
    """新业务逻辑"""
    pass
```

2. **添加测试** (`tests/services/test_new_service.py`)
```python
def test_new_business_logic():
    result = new_business_logic({"key": "value"})
    assert result is not None
```

### 添加前端页面

1. **创建页面** (`frontend/src/views/NewPage.vue`)
2. **添加路由** (`frontend/src/router/index.js`)
```javascript
{
  path: '/new-page',
  name: 'NewPage',
  component: () => import('@/views/NewPage.vue')
}
```

---

## ✅ 代码质量检查清单

### 提交前检查

- [ ] 代码符合PEP 8（Python）/ ESLint（JavaScript）
- [ ] 所有函数有类型提示
- [ ] 所有公共函数有文档字符串
- [ ] 添加了单元测试
- [ ] 测试全部通过
- [ ] 没有console.log（生产环境）
- [ ] 没有TODO注释（或已记录issue）
- [ ] 更新了相关文档

### 代码审查要点

- [ ] 单一职责原则
- [ ] 命名清晰有意义
- [ ] 避免过深嵌套（< 4层）
- [ ] 函数长度适中（< 50行）
- [ ] 没有重复代码
- [ ] 错误处理完善
- [ ] 安全性考虑（输入验证、SQL注入等）

---

## 📚 参考资源

### 代码风格
- Python: [PEP 8](https://pep8.org/)
- JavaScript: [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Vue: [Vue Style Guide](https://vuejs.org/style-guide/)

### 架构模式
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Twelve-Factor App](https://12factor.net/)

---

**创建时间**: 2026-07-10  
**维护**: 开发团队  
**版本**: v1.0
