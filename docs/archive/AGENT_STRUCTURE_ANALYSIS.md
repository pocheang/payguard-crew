# Agent代码结构问题分析

**发现日期**: 2026-06-28  
**问题**: Agent代码分散在两个目录

---

## 🔍 当前结构问题

### 问题：代码分散

```
app/
├── agents/                    # 旧位置
│   ├── agent_factory.py       # Agent工厂
│   ├── llm_client.py          # LLM客户端
│   ├── prompts.py             # 旧Prompt定义
│   └── prompts/               # 新Prompt目录
│       ├── transaction_agent.py
│       ├── fraud_detection_agent.py
│       └── ... (9个prompt文件)
│
└── crew/
    └── agents/                # 新位置（实际运行逻辑）
        ├── core_agents.py     # 核心Agent运行器
        ├── risk_agents.py     # 风险Agent运行器
        └── evidence_agents.py # 证据Agent运行器
```

**混乱点**:
- ✅ **Prompts**: 在 `app/agents/prompts/` - 清晰
- ⚠️ **运行逻辑**: 在 `app/crew/agents/` - 位置不直观
- ⚠️ **工厂模式**: 在 `app/agents/` - 分散

---

## 💡 建议的统一方案

### 方案A: 全部移到 app/agents/ (推荐)

```
app/agents/
├── __init__.py
├── factory.py              # 重命名 agent_factory.py
├── llm_client.py           # 保持不变
├── prompts/                # 保持不变
│   └── ... (9个文件)
└── runners/                # 新增：从crew/agents移入
    ├── __init__.py
    ├── core.py             # 重命名 core_agents.py
    ├── risk.py             # 重命名 risk_agents.py
    └── evidence.py         # 重命名 evidence_agents.py
```

**优点**:
- ✅ 所有Agent相关代码集中
- ✅ 层次清晰：prompts → runners → factory
- ✅ 符合直觉

---

### 方案B: 保持现状但明确职责 (保守)

```
app/agents/                 # 定义层
├── factory.py              # Agent创建
├── llm_client.py           # LLM调用
└── prompts/                # Prompt模板

app/crew/agents/            # 执行层
├── core_agents.py          # 核心Agent执行
├── risk_agents.py          # 风险Agent执行  
└── evidence_agents.py      # 证据Agent执行
```

**优点**:
- ✅ 不需要大改动
- ✅ 分层明确（定义 vs 执行）

---

## 🎯 我的推荐

### 使用方案A（统一到app/agents/）

**理由**:
1. **更直观**: 找Agent相关代码只需看一个目录
2. **更清晰**: runners/下是执行逻辑，prompts/下是模板
3. **更易维护**: 不用在两个目录间跳转

**迁移步骤**:
1. 创建 `app/agents/runners/`
2. 移动 `app/crew/agents/*.py` → `app/agents/runners/`
3. 重命名文件（可选）
4. 更新所有导入
5. 删除 `app/crew/agents/`

---

## ❓ 你的选择

请选择：
- **方案A**: 统一到 `app/agents/` (推荐，需要迁移)
- **方案B**: 保持现状 (保守，仅文档化)
- **其他**: 自定义方案

---

**当前状态**: 等待决策
