# PayGuard Crew 支付风控与合规审核多智能体系统开发设计文档

## 1. 项目定位

**PayGuard Crew** 是一个面向支付风控、合规审核和流程自动化场景的 AI Agent Demo 项目。

项目使用 **模拟交易数据 + 自建合规知识库 + CrewAI 多智能体编排 + FastAPI 接口 + 规则引擎 + RAG 检索**，实现对交易的自动审核，包括：

- 交易异常识别
- 风控规则匹配
- AML / KYC 合规校验
- 知识库证据检索
- 风险评分与风险分级
- 审核报告生成
- 人工复核建议
- 审计日志保存

> 注意：本项目是个人 Demo / 原型系统，不接入真实支付接口，不使用真实用户隐私数据，不替代真实生产风控系统。

---

## 2. 简历项目名称

**PayGuard Crew 支付风控与合规审核多智能体系统｜AI Agent Demo**

---

## 3. 推荐简历描述

- 基于 **CrewAI + LangChain + FastAPI** 构建支付风控审核原型系统，使用模拟交易数据与自建合规知识库，将审核流程拆解为交易分析、规则匹配、合规校验、证据检索与报告生成等 Agent 任务。
- 设计**规则优先、模型辅助**的审核链路，结合账户年龄、交易金额、交易频次、IP 异常、KYC 状态、设备状态、商户风险等级等特征输出风险评分、触发规则与处置建议。
- 构建 **RAG 检索模块**，接入支付风控规则、AML/KYC 审核手册、商户管理规范和人工复核流程文档，支持生成带引用依据的审核报告。
- 封装 **FastAPI 审核接口**，支持输入交易流水并返回风险等级、审核理由、证据来源、人工复核建议和审计日志，提升系统可解释性与工程可展示性。

---

## 4. 技术栈

| 模块 | 技术 |
|---|---|
| API 服务 | FastAPI, Uvicorn |
| 多 Agent 编排 | CrewAI |
| LLM 接入 | DeepSeek API / OpenAI API / Qwen API / Ollama |
| Schema 校验 | Pydantic |
| 规则引擎 | Python |
| RAG 检索 | LangChain, ChromaDB |
| 数据存储 | SQLite |
| 文档知识库 | Markdown |
| 测试 | Pytest |
| 部署 | Docker |

---

## 5. 系统架构

```text
用户 / API 调用方
        ↓
FastAPI 接口层
        ↓
Pydantic 参数校验
        ↓
CrewAI 多智能体编排层
        ↓
------------------------------------------------
| Router Agent              任务类型判断        |
| Transaction Agent         交易行为分析        |
| Risk Rule Agent           风控规则匹配        |
| Compliance Agent          AML / KYC 合规校验  |
| RAG Evidence Agent        知识库证据检索      |
| Report Agent              审核报告生成        |
------------------------------------------------
        ↓
规则引擎 + RAG 检索 + LLM 总结
        ↓
SQLite 审核记录 / 审计日志
        ↓
结构化审核结果 JSON
```

---

## 6. 核心流程

```text
1. 输入一笔模拟交易
2. FastAPI 校验交易字段
3. 风控规则引擎计算 risk_score 和 triggered_rules
4. Compliance Agent 判断 KYC / AML 风险
5. RAG Evidence Agent 检索相关规则依据
6. Report Agent 汇总最终报告
7. SQLite 保存审核结果和执行日志
8. API 返回结构化 JSON
```

---

## 7. Agent 设计

### 7.1 Router Agent

职责：

- 判断任务类型
- 决定是否进入交易审核流程
- 后续可扩展：商户审核、账户审核、人工复核报告生成

### 7.2 Transaction Agent

职责：

- 分析交易金额、频次、账户年龄、IP、设备、商户风险等行为特征
- 输出交易行为风险点

### 7.3 Risk Rule Agent

职责：

- 执行确定性规则
- 计算风险分数
- 输出触发规则
- 规则优先于模型判断

### 7.4 Compliance Agent

职责：

- 检查 KYC 状态
- 判断是否存在 AML 可疑行为
- 判断是否需要人工复核

### 7.5 RAG Evidence Agent

职责：

- 从 Markdown 知识库中检索相关规则
- 返回 source、content、score
- 为最终报告提供证据依据

### 7.6 Report Agent

职责：

- 汇总规则结果、合规结果、RAG 证据
- 生成最终审核报告
- 输出 risk_level、risk_score、decision、summary、suggestion

---

## 8. 数据字段设计

### 8.1 输入交易 JSON

```json
{
  "transaction_id": "TX20260623001",
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
  "timestamp": "2026-06-23T10:30:00"
}
```

### 8.2 输出审核 JSON

```json
{
  "transaction_id": "TX20260623001",
  "risk_level": "high",
  "risk_score": 95,
  "decision": "review",
  "summary": "该交易涉及新账户大额交易、高频交易、IP异常和设备异常，综合判断为高风险。",
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
      "content": "新注册账户在7天内发生单笔超过5000元交易，应标记为中高风险。"
    }
  ],
  "suggestion": "建议暂缓交易并进入人工复核流程。",
  "requires_manual_review": true
}
```

---

## 9. 风控规则设计

| 规则 ID | 条件 | 分数 |
|---|---|---|
| R001 | account_age_days < 7 且 amount > 5000 | +25 |
| R002 | transaction_frequency_1h > 10 | +20 |
| R003 | ip_location_status = abnormal | +15 |
| R004 | kyc_status != verified 且 amount > 3000 | +20 |
| R005 | merchant_risk_level = high | +25 |
| R006 | device_status = abnormal | +15 |
| R007 | is_blacklisted = true | 直接 high / reject |

### 风险等级

```text
0 - 29   low
30 - 69  medium
70 - 100 high
```

### 决策映射

```text
low      approve
medium   review
high     review / hold
blacklist reject
```

---

## 10. API 设计

### 10.1 健康检查

```http
GET /health
```

### 10.2 交易审核

```http
POST /audit/transaction
```

### 10.3 查询审核记录

```http
GET /audit/report/{transaction_id}
```

### 10.4 查询审计日志

```http
GET /audit/logs/{transaction_id}
```

---

## 11. 项目目录结构

```text
payguard-crew/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── audit.py
│   ├── schemas/
│   │   ├── transaction.py
│   │   └── audit.py
│   ├── rules/
│   │   └── risk_rules.py
│   ├── agents/
│   │   ├── prompts.py
│   │   └── agent_factory.py
│   ├── crew/
│   │   └── audit_crew.py
│   ├── rag/
│   │   ├── simple_retriever.py
│   │   └── ingest.py
│   ├── db/
│   │   ├── database.py
│   │   └── repository.py
│   └── utils/
│       └── time.py
├── docs/
├── data/
├── tests/
├── scripts/
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

## 12. 开发阶段

### 第一阶段：最小可运行版本

目标：

- FastAPI 可启动
- POST /audit/transaction 可返回结果
- 规则引擎可运行
- 示例数据可测试

### 第二阶段：加入 RAG

目标：

- docs Markdown 可检索
- 返回 evidence 来源
- 支持简单关键词检索，后续升级 ChromaDB

### 第三阶段：加入 CrewAI

目标：

- 使用 CrewAI Agent / Task / Crew 编排
- 多 Agent 输出审计日志
- Report Agent 生成更自然的审核摘要

### 第四阶段：工程化增强

目标：

- SQLite 存储审核报告
- Docker 部署
- Pytest 测试
- README 完整说明
- Codex 继续补全 ChromaDB、LLM、SSE 前端

---

## 13. 本项目已生成的代码范围

当前 starter 版本已经包含：

- FastAPI 项目骨架
- Pydantic Schema
- 风险规则引擎
- 简单 Markdown 检索器
- 交易审核 API
- 示例交易数据
- 示例知识库文档
- CrewAI 待补全骨架
- README 运行说明
- Codex 任务说明

Codex 需要继续完成：

- 真正的 CrewAI Agent / Task / Crew 接入
- DeepSeek / OpenAI / Ollama LLM 配置
- ChromaDB 向量检索
- SQLite 审计日志完整保存
- 单元测试
- Docker 完善
- 可选前端或 SSE 执行轨迹展示

---

## 14. 交给 Codex 的开发指令

请基于当前项目骨架继续完成 PayGuard Crew。

优先级如下：

1. 保持现有 FastAPI 接口可运行，不要破坏 POST /audit/transaction。
2. 补全 app/crew/audit_crew.py，引入 CrewAI Agent、Task、Crew。
3. 将 Risk Rule Agent 与现有 app/rules/risk_rules.py 对接，确保规则判断仍由确定性代码完成。
4. 将 RAG Evidence Agent 与 app/rag/simple_retriever.py 对接，后续可升级为 ChromaDB。
5. 新增 LLM 配置，支持 DeepSeek API 或 OpenAI API，API Key 从 .env 读取。
6. 补全 SQLite 存储，包括 audit_reports、audit_logs、rule_hits。
7. 新增 pytest 测试：规则测试、API 测试、RAG 测试。
8. 完善 README，写明安装、配置、启动、测试接口。
9. 保持项目定位为 Demo，不要写入真实支付接口或真实用户数据。
10. 所有输出 JSON 必须通过 Pydantic 校验。
