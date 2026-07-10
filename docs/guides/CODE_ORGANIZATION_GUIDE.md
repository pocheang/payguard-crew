# 项目代码组织指南

> **版本**: v0.2.0  
> **更新**: 2026-07-10  
> **目标**: 保持代码清晰、模块化、易于扩展  
> **原则**: 单一职责、高内聚低耦合、可测试

---

## 📁 实际项目结构

### 后端结构（app/）

```
app/
├── __init__.py
├── main.py                  # ⭐ FastAPI应用入口
├── config.py                # ⭐ 配置管理（环境变量、验证）
│
├── agents/                  # 🤖 AI Agent系统
│   ├── agent_factory.py     # Agent工厂
│   ├── llm_client.py        # LLM客户端
│   ├── prompts/             # Agent提示词
│   │   ├── compliance_agent.py
│   │   ├── fraud_detection_agent.py
│   │   ├── risk_rule_agent.py
│   │   └── ...
│   └── runners/             # Agent运行器
│       ├── base.py
│       ├── core.py
│       └── risk.py
│
├── api/                     # 🔌 API路由层
│   ├── audit.py             # 审计接口
│   ├── review.py            # 审核接口
│   ├── rules.py             # 规则管理
│   ├── batch.py             # 批量操作
│   ├── websocket.py         # WebSocket
│   ├── auth.py              # 认证接口
│   ├── health.py            # 健康检查
│   ├── metrics.py           # 指标接口
│   ├── dependencies.py      # 依赖注入
│   └── error_handler.py     # 错误处理
│
├── core/                    # ⚙️ 核心功能
│   ├── auth.py              # 认证核心
│   ├── cache.py             # 缓存管理
│   ├── environment.py       # 环境检测
│   ├── lifecycle.py         # 生命周期
│   ├── llm_config.py        # LLM配置
│   ├── logging.py           # 日志配置
│   ├── metrics.py           # 性能指标
│   ├── middlewares.py       # 中间件
│   ├── monitoring.py        # 监控
│   ├── task_queue.py        # 任务队列
│   ├── tracing.py           # 追踪
│   ├── websocket.py         # WebSocket核心
│   └── exception_handlers.py
│
├── services/                # 📦 业务逻辑层
│   ├── audit_service.py     # 审计服务
│   ├── review_service.py    # 审核服务
│   ├── rule_service.py      # 规则服务
│   └── ...
│
├── db/                      # 💾 数据访问层
│   ├── database.py          # 数据库连接
│   ├── models.py            # SQLAlchemy模型
│   ├── repositories.py      # 数据仓库
│   ├── query_optimizer.py   # 查询优化
│   └── migrations/          # 数据库迁移
│
├── auth/                    # 🔐 认证授权
│   └── api_key.py           # API Key验证
│
├── compliance/              # 📋 合规模块
│   ├── aml_service.py       # 反洗钱
│   ├── kyc_service.py       # KYC验证
│   ├── audit_trail.py       # 审计追踪
│   └── regulatory_reporting.py
│
├── security/                # 🛡️ 安全模块
│   └── validators.py        # 输入验证
│
├── rules/                   # ⚖️ 规则引擎
│   └── engine.py            # 规则引擎核心
│
├── crew/                    # 👥 CrewAI集成
│   └── ...                  # Crew配置
│
├── rag/                     # 🔍 RAG检索增强
│   └── ...                  # 向量检索
│
├── middleware/              # 🔧 中间件
│   └── rate_limit.py        # 速率限制
│
├── schemas/                 # 📝 Pydantic模型
│   ├── transaction.py       # 交易模型
│   ├── audit.py             # 审计模型
│   └── ...
│
├── utils/                   # 🛠️ 工具函数
│   ├── batch_processor.py   # 批处理
│   ├── datetime_utils.py    # 时间工具
│   └── validators.py        # 验证工具
│
└── data/                    # 📊 数据文件
    └── ...
```

### 前端结构（frontend/）

```
frontend/
├── src/
│   ├── main.js              # ⭐ 应用入口
│   ├── App.vue              # ⭐ 根组件
│   │
│   ├── assets/              # 🎨 静态资源
│   │   └── responsive.css   # 响应式样式
│   │
│   ├── components/          # 🧩 Vue组件
│   │   ├── charts/          # 图表组件（ECharts）
│   │   │   ├── RiskTrendChart.vue
│   │   │   ├── TransactionPieChart.vue
│   │   │   ├── ReviewWorkloadChart.vue
│   │   │   └── TimeSeriesChart.vue
│   │   ├── Chart.vue        # 图表基础组件
│   │   └── StatisticsCharts.vue
│   │
│   ├── views/               # 📄 页面组件
│   │   ├── Dashboard.vue    # 主Dashboard
│   │   └── DashboardImproved.vue
│   │
│   ├── router/              # 🛣️ 路由配置
│   │   └── index.js
│   │
│   ├── services/            # 🔗 服务层
│   │   ├── api.js           # API调用
│   │   └── websocket.js     # WebSocket客户端
│   │
│   ├── stores/              # 📦 状态管理（Pinia）
│   │   └── ...
│   │
│   ├── utils/               # 🛠️ 工具函数
│   │   └── logger.js        # 日志工具
│   │
│   └── tests/               # 🧪 前端测试
│       └── unit.test.js
│
├── public/                  # 公共资源
├── package.json             # 依赖配置
├── vite.config.js           # ⚙️ Vite配置（代码分割）
└── index.html
```

### 测试结构（tests/）

```
tests/
├── __init__.py
├── conftest.py              # Pytest配置
│
├── api/                     # API测试
│   ├── test_audit.py        # 审计API测试
│   └── test_review.py       # 审核API测试
│
├── services/                # 服务层测试
│   └── ...
│
├── test_review_enhancements.py
└── test_review_workflow.py
```

### 文档结构（docs/）

```
docs/
├── README.md                # 📚 文档索引
├── REPORT_ORGANIZATION.md   # 报告整理指南
│
├── api/                     # 🔌 API文档
│   └── API_DOCUMENTATION.md
│
├── guides/                  # 📖 使用指南（24个）
│   ├── QUICK_START.md
│   ├── DOCKER.md            # Docker完整指南
│   ├── DEMO.md              # 演示指南
│   ├── CODE_ORGANIZATION_GUIDE.md  # 本文档
│   └── ...
│
├── reports/                 # 📊 技术报告（14个）
│   ├── README.md            # 报告索引
│   ├── PROJECT_SUMMARY.md   # 项目综合报告
│   └── ...
│
├── architecture/            # 🏗️ 架构文档（4个）
│   ├── SYSTEM_COMPLETE.md
│   └── ...
│
└── archive/                 # 📦 历史文档（16个）
    ├── README.md
    └── ...
```

---

## 🎯 代码组织原则

### 1. 分层架构

```
API层 (app/api/)
    ↓ 调用
服务层 (app/services/)
    ↓ 调用
数据层 (app/db/)
```

**示例**:
```python
# ✅ 清晰的分层
# app/api/audit.py - API层
@router.post("/audit/transaction")
def audit_transaction_endpoint(tx: TransactionRequest):
    result = audit_service.audit(tx)  # 调用服务层
    return result

# app/services/audit_service.py - 服务层
def audit(tx: TransactionRequest) -> AuditResult:
    rules = rule_repository.get_active()  # 调用数据层
    score = calculate_risk(tx, rules)
    return AuditResult(score=score)

# app/db/repositories.py - 数据层
def get_active_rules() -> List[Rule]:
    return db.query(Rule).filter(Rule.active == True).all()
```

### 2. 单一职责原则

每个模块只负责一件事：

- **API层**: HTTP请求/响应处理
- **Services层**: 业务逻辑
- **DB层**: 数据持久化
- **Core**: 基础设施（日志、缓存、配置）
- **Utils**: 纯函数工具

```python
# ❌ 职责混乱
@router.post("/audit")
def audit(tx: dict):
    # 混合了验证、业务逻辑、数据访问
    if not tx.get("amount"):
        return {"error": "Invalid"}
    score = tx["amount"] * 0.1  # 业务逻辑
    db.execute("INSERT...")      # 数据访问
    return {"score": score}

# ✅ 职责清晰
@router.post("/audit")
def audit(tx: TransactionRequest):  # Pydantic自动验证
    result = audit_service.audit(tx)  # 服务层处理业务
    return result  # 只负责HTTP
```

### 3. 依赖注入

使用FastAPI的Depends进行依赖注入：

```python
# app/api/dependencies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

# app/api/audit.py
@router.get("/audits")
def list_audits(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return fetch_audits(db, user)
```

### 4. 类型提示

所有函数都应有完整的类型提示：

```python
# ✅ 完整的类型提示
from typing import List, Optional, Dict

def get_reviews(
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, any]]:
    """获取审核列表"""
    pass

# ❌ 缺少类型提示
def get_reviews(assigned_to=None, limit=100):
    pass
```

---

## 🔧 前端组织规范

### 组件分类

**按需导入ECharts**（性能优化）:
```javascript
// ✅ 按需导入（-98.6%体积）
import { init, use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([TitleComponent, TooltipComponent, LineChart, CanvasRenderer])

// ❌ 完整导入（1050KB）
import * as echarts from 'echarts'
```

### 组件命名规范

```javascript
// ✅ 多词组件名（避免与HTML标签冲突）
export default {
  name: 'RiskTrendChart'     // 好
}

// ❌ 单词组件名
export default {
  name: 'Chart'              // 可能冲突
}
```

### API服务层

```javascript
// frontend/src/services/api.js
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default {
  // 审计API
  auditTransaction(data) {
    return axios.post(`${API_BASE_URL}/audit/transaction`, data)
  },
  
  // 审核API
  getReviews(params) {
    return axios.get(`${API_BASE_URL}/review/list/pending`, { params })
  }
}
```

---

## 📦 模块导入规范

### Python导入顺序

```python
# 1. 标准库
import os
import sys
from pathlib import Path
from typing import List, Optional

# 2. 第三方库
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 3. 本地模块
from app.config import get_settings
from app.db.database import get_db
from app.services.audit_service import audit_transaction
```

### JavaScript导入顺序

```javascript
// 1. Vue核心
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// 2. 第三方库
import axios from 'axios'
import { init, use } from 'echarts/core'

// 3. 本地模块
import api from '@/services/api'
import logger from '@/utils/logger'
```

---

## 🧪 测试组织

### 测试文件对应

```
app/api/audit.py → tests/api/test_audit.py
app/services/audit_service.py → tests/services/test_audit_service.py
```

### 测试命名规范

```python
# ✅ 描述性测试名
def test_audit_transaction_success():
    """测试：成功审计交易"""
    pass

def test_audit_transaction_invalid_amount_raises_error():
    """测试：无效金额抛出错误"""
    pass

# ❌ 模糊的测试名
def test_audit():
    pass
```

### 测试覆盖

当前测试覆盖率：**60%+**

运行测试：
```bash
# 所有测试
pytest

# 带覆盖率
pytest --cov=app --cov-report=html

# 特定测试
pytest tests/api/test_audit.py -v
```

---

## 🗂️ 配置文件

```
.
├── .env.example          # 配置模板
├── .env.development      # 开发配置（已添加）
├── .env.production       # 生产配置（已添加）
├── .gitignore            # Git忽略
├── pytest.ini            # Pytest配置
├── requirements.txt      # Python依赖
├── docker-compose.yml    # Docker编排
├── Dockerfile            # Docker镜像
└── Makefile              # 自动化命令
```

---

## 🚀 扩展指南

### 添加新API接口

**1. 创建路由**（`app/api/new_feature.py`）:
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/new", tags=["new-feature"])

@router.post("/")
def create_new(data: dict):
    return {"status": "created"}
```

**2. 注册路由**（`app/main.py`）:
```python
from app.api.new_feature import router as new_router

app.include_router(new_router, prefix="/api/new")
```

**3. 添加测试**（`tests/api/test_new_feature.py`）:
```python
def test_create_new():
    response = client.post("/api/new/")
    assert response.status_code == 200
```

### 添加新服务

**1. 创建服务**（`app/services/new_service.py`）:
```python
from typing import Dict

def process_data(data: Dict) -> Dict:
    """处理数据"""
    # 业务逻辑
    return {"result": "processed"}
```

**2. 添加测试**（`tests/services/test_new_service.py`）:
```python
from app.services.new_service import process_data

def test_process_data():
    result = process_data({"input": "test"})
    assert result["result"] == "processed"
```

### 添加前端页面

**1. 创建页面**（`frontend/src/views/NewPage.vue`）:
```vue
<template>
  <div>
    <h1>New Page</h1>
  </div>
</template>

<script setup>
// 逻辑代码
</script>
```

**2. 添加路由**（`frontend/src/router/index.js`）:
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

- [ ] **代码格式**: 符合PEP 8（Python）/ ESLint（JavaScript）
- [ ] **类型提示**: 所有函数有类型提示
- [ ] **文档**: 所有公共函数有文档字符串
- [ ] **测试**: 添加了单元测试
- [ ] **测试通过**: 所有测试通过
- [ ] **生产代码**: 无console.log/print调试语句
- [ ] **TODO**: 无未解决的TODO注释
- [ ] **文档更新**: 更新了相关文档
- [ ] **Git**: Commit消息符合规范

### 代码审查要点

- [ ] **单一职责**: 每个函数/模块职责清晰
- [ ] **命名**: 命名清晰有意义
- [ ] **嵌套**: 避免过深嵌套（< 4层）
- [ ] **函数长度**: 函数适中（< 50行）
- [ ] **DRY**: 没有重复代码
- [ ] **错误处理**: 错误处理完善
- [ ] **安全**: 输入验证、SQL注入防护
- [ ] **性能**: 无明显性能问题

---

## 📊 项目统计

### 代码规模（v0.2.0）

```
Language      Files    Lines    Code
--------------------------------------
Python          45     5,234   3,890
JavaScript      38     4,156   3,245
Vue             12     2,891   2,234
Markdown        64     ~9000   ~9000
--------------------------------------
Total          159    21,281  18,369
```

### 文档组织

- **guides/**: 24个使用指南
- **reports/**: 14个技术报告
- **architecture/**: 4个架构文档
- **archive/**: 16个历史文档

---

## 📚 参考资源

### 代码风格
- [PEP 8](https://pep8.org/) - Python代码风格
- [Airbnb Style Guide](https://github.com/airbnb/javascript) - JavaScript风格
- [Vue Style Guide](https://vuejs.org/style-guide/) - Vue最佳实践

### 架构模式
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Twelve-Factor App](https://12factor.net/)

### 项目文档
- [项目主页](../../README.md)
- [贡献指南](../../CONTRIBUTING.md)
- [文档中心](../README.md)

---

**创建时间**: 2026-07-10  
**最后更新**: 2026-07-10  
**维护**: PayGuard开发团队  
**版本**: v0.2.0
