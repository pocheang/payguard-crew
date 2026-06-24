# PayGuard Crew - AI Multi-Agent 支付风控与合规审计系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.80+-orange.svg)](https://www.crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

PayGuard Crew 是一个基于 **AI Multi-Agent** 架构的支付风控与合规审计演示系统，展示了如何将 **规则引擎** 与 **大语言模型** 结合，构建可靠的金融风控解决方案。

## 📋 目录

- [项目介绍](#项目介绍)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [核心功能](#核心功能)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [API 使用示例](#api-使用示例)
- [风控规则说明](#风控规则说明)
- [Agent 职责说明](#agent-职责说明)
- [设计理念](#设计理念)
- [扩展方向](#扩展方向)
- [简历项目描述](#简历项目描述)

---

## 项目介绍

PayGuard Crew 是一个演示性质的支付风控系统，使用 **Multi-Agent 协作** 模式处理交易审计流程。系统采用 **规则优先、模型辅助** 的设计理念，确保核心风控决策由确定性规则引擎完成，AI Agent 负责证据检索、报告生成和审计日志记录。

### 为什么是 Demo？

- ❌ **不接入真实支付网关** - 所有交易数据均为模拟
- ❌ **不处理真实用户隐私数据** - 无 PII（个人身份信息）
- ✅ **硬风控决策由代码实现** - 规则引擎保证确定性
- ✅ **LLM 仅用于辅助解释** - 生成报告文本和建议

### 适用场景

- 🎓 学习 AI Agent 和 Multi-Agent 系统开发
- 💼 展示金融科技领域的技术能力
- 🔬 探索 RAG（检索增强生成）在风控场景的应用
- 📚 了解支付风控、AML、KYC 合规流程

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Server                            │
│                  (Transaction Audit API)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Audit Crew Orchestrator     │
         │   (Multi-Agent Workflow)      │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌──────────┐ ┌─────────────┐
│ Transaction    │ │ Evidence │ │   Report    │
│    Agent       │ │  Agent   │ │   Agent     │
│                │ │          │ │             │
│ • 解析交易     │ │ • 检索   │ │ • 生成报告  │
│ • 提取特征     │ │   政策   │ │ • 格式化    │
└───────┬────────┘ └─────┬────┘ └──────┬──────┘
        │                │              │
        ▼                ▼              ▼
┌────────────────────────────────────────────────┐
│           Risk Rule Engine (Python)            │
│  • R001: 新账户大额交易                         │
│  • R002: 高频交易                               │
│  • R003: IP 地址异常                            │
│  • R004: KYC 未完整                             │
│  • R005: 高风险商户                             │
│  • R006: 设备异常                               │
│  • R007: 黑名单命中                             │
└────────────────┬───────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
┌──────────┐ ┌──────┐ ┌─────────────┐
│ ChromaDB │ │SQLite│ │   Docs/     │
│ (Vector) │ │ (DB) │ │ (知识库)    │
│          │ │      │ │             │
│ • 政策   │ │• 报告│ │ • KYC 政策  │
│   检索   │ │• 日志│ │ • AML 指南  │
│ • RAG    │ │• 规则│ │ • 风险规则  │
└──────────┘ └──────┘ └─────────────┘
```

---

## 技术栈

### 后端框架
- **FastAPI** - 高性能异步 Web 框架
- **Pydantic** - 数据验证和序列化
- **SQLite** - 轻量级关系数据库

### AI Agent & LLM
- **CrewAI** - Multi-Agent 编排框架
- **OpenAI API** - GPT 模型支持
- **DeepSeek API** - 国产大模型支持
- **Ollama** - 本地模型运行

### RAG & 向量检索
- **ChromaDB** - 向量数据库
- **本地哈希嵌入** - 离线向量化方案
- **Markdown** - 知识库文档格式

### 开发工具
- **Pytest** - 单元测试和集成测试
- **Python-dotenv** - 环境变量管理
- **Uvicorn** - ASGI 服务器

---

## 核心功能

### 1. 交易风险评估
- ✅ 实时交易风控规则引擎
- ✅ 7 大类风险规则（R001-R007）
- ✅ 风险评分计算（0-100）
- ✅ 风险等级分类（low/medium/high）
- ✅ 决策输出（approve/review/hold/reject）

### 2. 合规审计
- ✅ KYC（Know Your Customer）身份验证
- ✅ AML（Anti-Money Laundering）反洗钱检查
- ✅ 黑名单筛查
- ✅ 设备指纹和 IP 地址分析

### 3. RAG 知识库检索
- ✅ ChromaDB 向量检索
- ✅ 政策文档智能匹配
- ✅ 自动 fallback 到关键词检索
- ✅ 中英文混合支持

### 4. Multi-Agent 协作
- ✅ Transaction Agent - 交易解析
- ✅ Evidence Agent - 证据检索
- ✅ Report Agent - 报告生成
- ✅ CrewAI 任务编排（可选）

### 5. 审计日志
- ✅ 完整的 Agent 执行日志
- ✅ 规则命中记录
- ✅ 审计报告持久化
- ✅ 人工复核追溯

---

## 项目结构

```
payguard_crew_starter/
├── app/
│   ├── agents/              # AI Agent 定义
│   │   ├── agent_factory.py # Agent 工厂
│   │   ├── llm_client.py    # LLM 客户端
│   │   └── prompts.py       # Prompt 模板
│   ├── api/                 # FastAPI 路由
│   │   └── audit.py         # 审计 API
│   ├── crew/                # CrewAI 编排
│   │   └── audit_crew.py    # 审计 Crew
│   ├── db/                  # 数据库
│   │   ├── database.py      # SQLite 连接
│   │   └── repository.py    # 数据访问层
│   ├── rag/                 # RAG 检索
│   │   ├── ingest.py        # 文档索引
│   │   ├── retriever.py     # 统一检索接口
│   │   ├── simple_retriever.py  # 关键词检索
│   │   └── vector_store.py  # ChromaDB 封装
│   ├── rules/               # 风控规则
│   │   └── risk_rules.py    # 规则引擎
│   ├── schemas/             # 数据模型
│   │   ├── audit.py         # 审计响应模型
│   │   └── transaction.py   # 交易模型
│   ├── config.py            # 配置管理
│   └── main.py              # FastAPI 应用入口
├── docs/                    # 知识库
│   ├── kyc_policy.md        # KYC 政策
│   ├── aml_review_guide.md  # AML 审核指南
│   ├── payment_risk_rules.md# 支付风险规则
│   ├── merchant_risk_policy.md # 商户风险政策
│   └── manual_review_process.md # 人工复核流程
├── scripts/
│   └── ingest_docs.py       # 知识库索引脚本
├── tests/                   # 测试套件
│   ├── test_rules.py        # 规则引擎测试
│   ├── test_api.py          # API 测试
│   ├── test_rag.py          # RAG 测试
│   └── test_db.py           # 数据库测试
├── data/
│   └── sample_transaction.json # 示例交易
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量模板
└── README.md                # 项目文档
```

---

## 快速开始

### 1. 环境要求

- Python 3.9+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改：

```env
# 应用配置
APP_NAME=payguard-crew
APP_ENV=dev

# LLM 配置（可选，不配置则使用规则引擎模式）
LLM_PROVIDER=deepseek              # 选项: openai, deepseek, ollama, disabled
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=

OLLAMA_MODEL=qwen2.5
OLLAMA_BASE_URL=http://localhost:11434/v1

# CrewAI 配置
ENABLE_CREWAI=false                # 是否启用 CrewAI 编排

# RAG 配置
RAG_TOP_K=3                        # 检索返回数量
PAYGUARD_DOCS_DIR=docs             # 知识库目录

# 数据库配置
SQLITE_DB_PATH=./payguard_crew.db  # SQLite 数据库路径

# LLM 超时配置
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
```

#### 配置说明

**LLM_PROVIDER 选项：**

- `disabled` - 仅使用规则引擎，不调用 LLM（推荐用于演示）
- `deepseek` - 使用 DeepSeek API（需要 DEEPSEEK_API_KEY）
- `openai` - 使用 OpenAI API（需要 OPENAI_API_KEY）
- `ollama` - 使用本地 Ollama（需要先安装 Ollama）

**ENABLE_CREWAI 说明：**

- `false` - 使用本地工作流（推荐，速度快）
- `true` - 使用 CrewAI 编排（需要 LLM，生成更详细的报告）

**容错机制：**

如果 LLM 不可用或配置错误，系统会自动 fallback 到规则引擎模式，不会崩溃。

### 4. 知识库入库

将 `docs/` 目录下的 Markdown 文档索引到 ChromaDB：

```bash
python scripts/ingest_docs.py
```

预期输出：
```
Indexed 14 chunks from 5 docs into payguard_docs at C:\...\payguard_crew_starter\.chroma
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

访问 API 文档：
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 6. 运行测试

```bash
pytest -q
```

---

## Docker 部署

### 方式一：使用 Docker 命令

#### 1. 构建镜像

```bash
docker build -t payguard-crew .
```

#### 2. 运行容器

```bash
docker run -d \
  --name payguard-crew \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/docs:/app/docs \
  -v $(pwd)/.chroma:/app/.chroma \
  -v $(pwd)/payguard_crew.db:/app/payguard_crew.db \
  payguard-crew
```

Windows PowerShell:
```powershell
docker run -d `
  --name payguard-crew `
  -p 8000:8000 `
  --env-file .env `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/docs:/app/docs `
  -v ${PWD}/.chroma:/app/.chroma `
  -v ${PWD}/payguard_crew.db:/app/payguard_crew.db `
  payguard-crew
```

#### 3. 查看日志

```bash
docker logs -f payguard-crew
```

#### 4. 停止容器

```bash
docker stop payguard-crew
docker rm payguard-crew
```

### 方式二：使用 Docker Compose（推荐）

#### 1. 启动服务

```bash
docker-compose up -d
```

#### 2. 查看日志

```bash
docker-compose logs -f
```

#### 3. 停止服务

```bash
docker-compose down
```

#### 4. 重新构建并启动

```bash
docker-compose up -d --build
```

### Docker 配置说明

#### 环境变量

容器会读取 `.env` 文件中的环境变量，主要配置项：

```env
# LLM 配置（可选）
LLM_PROVIDER=disabled    # 使用规则引擎模式，不调用 LLM
DEEPSEEK_API_KEY=        # 如需使用 DeepSeek，填入 API Key
OPENAI_API_KEY=          # 如需使用 OpenAI，填入 API Key

# CrewAI 配置
ENABLE_CREWAI=false      # 不启用 CrewAI，使用本地工作流

# 数据库路径
SQLITE_DB_PATH=/app/payguard_crew.db
```

#### 数据持久化

Docker Compose 会自动挂载以下目录，确保数据持久化：

- `./data` - 示例数据
- `./docs` - 知识库文档
- `./.chroma` - ChromaDB 向量数据库
- `./payguard_crew.db` - SQLite 数据库

#### 健康检查

容器启动后会自动进行健康检查：

```bash
# 检查容器健康状态
docker ps

# 手动健康检查
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "ok",
  "service": "payguard-crew"
}
```

### 索引知识库（Docker 环境）

容器启动后，进入容器执行索引：

```bash
# 方式一：Docker 命令
docker exec -it payguard-crew python scripts/ingest_docs.py

# 方式二：Docker Compose
docker-compose exec payguard-crew python scripts/ingest_docs.py
```

### 常见问题

#### 1. 端口已被占用

如果 8000 端口已被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 改为 8001
```

#### 2. 权限问题

如果遇到文件权限问题，确保挂载的目录有写权限：

```bash
chmod -R 755 data docs .chroma
```

#### 3. 查看容器内部

进入容器调试：

```bash
# Docker 命令
docker exec -it payguard-crew bash

# Docker Compose
docker-compose exec payguard-crew bash
```

---

## API 使用示例

### 健康检查

```bash
curl http://127.0.0.1:8000/health
```

**响应：**
```json
{
  "status": "ok",
  "service": "payguard-crew"
}
```

### 交易审计

```bash
curl -X POST http://127.0.0.1:8000/audit/transaction \
  -H "Content-Type: application/json" \
  -d @data/sample_transaction.json
```

或直接传递 JSON：

```bash
curl -X POST http://127.0.0.1:8000/audit/transaction \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**返回示例：**

```json
{
  "transaction_id": "TX20260623001",
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
    },
    {
      "rule_id": "R002",
      "rule_name": "high_frequency_transaction",
      "reason": "1小时内交易次数超过10次",
      "score": 20
    },
    {
      "rule_id": "R003",
      "rule_name": "abnormal_ip_location",
      "reason": "交易IP地区异常",
      "score": 15
    },
    {
      "rule_id": "R004",
      "rule_name": "incomplete_kyc_high_amount",
      "reason": "KYC未完整认证且交易金额超过3000",
      "score": 20
    },
    {
      "rule_id": "R006",
      "rule_name": "abnormal_device",
      "reason": "交易设备状态异常",
      "score": 15
    }
  ],
  "evidence": [
    {
      "source": "payment_risk_rules.md",
      "content": "## 新账户风险\n\n账户注册时间小于7天的用户，如果单笔交易金额超过5000元，需要触发风险审核..."
    },
    {
      "source": "kyc_policy.md",
      "content": "## KYC 认证等级\n\n- basic_verified: 基础认证，仅验证手机号\n- verified: 完整认证，包括身份证和人脸识别..."
    }
  ],
  "suggestion": "建议：1. 联系用户核实身份信息；2. 检查设备指纹是否存在异常；3. 复核交易目的和资金来源；4. 如发现可疑行为，立即冻结账户并上报。",
  "requires_manual_review": true
}
```

### 查询审计报告

```bash
curl http://127.0.0.1:8000/audit/report/TX20260623001
```

**响应：**
```json
{
  "transaction_id": "TX20260623001",
  "user_id": "U10086",
  "merchant_id": "M2033",
  "risk_score": 95,
  "risk_level": "high",
  "decision": "review",
  "summary": "交易触发多项高风险规则...",
  "suggestion": "建议：1. 联系用户核实身份信息...",
  "requires_manual_review": true,
  "created_at": "2026-06-23T10:35:22.123456+00:00",
  "triggered_rules": [...]
}
```

### 查询审计日志

```bash
curl http://127.0.0.1:8000/audit/logs/TX20260623001
```

**响应：**
```json
{
  "transaction_id": "TX20260623001",
  "logs": [
    {
      "agent_name": "transaction_agent",
      "input_data": "{\"transaction_id\": \"TX20260623001\", ...}",
      "output_data": "{\"parsed_features\": {...}}",
      "status": "completed",
      "error_message": null,
      "latency_ms": 45,
      "created_at": "2026-06-23T10:35:21.001234+00:00"
    },
    {
      "agent_name": "evidence_agent",
      "input_data": "{\"query\": \"新账户 高频交易 KYC\"}",
      "output_data": "{\"evidence_count\": 3}",
      "status": "completed",
      "error_message": null,
      "latency_ms": 120,
      "created_at": "2026-06-23T10:35:21.523456+00:00"
    },
    {
      "agent_name": "report_agent",
      "input_data": "{\"risk_score\": 95, ...}",
      "output_data": "{\"backend\": \"local\", \"report_length\": 456}",
      "status": "completed",
      "error_message": null,
      "latency_ms": 89,
      "created_at": "2026-06-23T10:35:22.012345+00:00"
    }
  ]
}
```

---

## 风控规则说明

系统实现了 7 大类确定性风控规则：

| 规则 ID | 规则名称 | 触发条件 | 风险评分 | 说明 |
|---------|---------|---------|---------|------|
| **R001** | 新账户大额交易 | 账户注册 < 7天 且 金额 > 5000 | +25 | 防范新账户欺诈 |
| **R002** | 高频交易 | 1小时内交易 > 10次 | +20 | 防范刷单和洗钱 |
| **R003** | IP 地址异常 | IP 地区异常 | +15 | 防范地理位置欺诈 |
| **R004** | KYC 未完整 | KYC 未完整 且 金额 > 3000 | +20 | 合规性要求 |
| **R005** | 高风险商户 | 商户风险等级为 high | +25 | 商户维度风控 |
| **R006** | 设备异常 | 设备状态异常 | +15 | 防范设备欺诈 |
| **R007** | 黑名单命中 | 用户/设备/商户在黑名单 | +100 | 直接拒绝 |

### 风险等级计算

```python
总评分 = sum(触发规则的评分)
风险等级 = {
    >= 70: "high",    # 高风险，需人工复核
    >= 30: "medium",  # 中风险，需人工复核
    < 30:  "low"      # 低风险，自动通过
}
```

### 决策逻辑

```python
if 黑名单命中:
    decision = "reject"  # 直接拒绝
elif 风险等级 == "high":
    decision = "review"  # 人工复核
elif 风险等级 == "medium":
    decision = "review"  # 人工复核
else:
    decision = "approve" # 自动通过
```

---

## Agent 职责说明

系统采用 **Multi-Agent 协作** 模式，每个 Agent 负责特定职责：

### 1. Transaction Agent（交易解析 Agent）
**职责：**
- 解析和验证交易数据
- 提取风险特征（金额、频率、账户年龄等）
- 调用规则引擎进行风险评分
- 输出结构化的风险评估结果

**输入：** 原始交易 JSON  
**输出：** 风险评分、触发规则列表、风险等级

### 2. Evidence Agent（证据检索 Agent）
**职责：**
- 根据触发的规则构建检索查询
- 从 ChromaDB 向量库检索相关政策文档
- Fallback 到关键词检索（如果向量检索失败）
- 返回最相关的 top_k 条证据

**输入：** 触发规则名称、交易特征  
**输出：** 证据列表（来源文档 + 内容片段）

### 3. Report Agent（报告生成 Agent）
**职责：**
- 整合风险评分、规则、证据
- 生成人类可读的审计报告
- 提供操作建议和复核要点
- 格式化输出为标准 JSON

**输入：** 风险评估结果 + 证据  
**输出：** 完整的审计报告（summary + suggestion）

### Agent 协作流程

```
用户请求
   ↓
Transaction Agent → 解析交易 → 调用规则引擎 → 计算风险评分
   ↓
Evidence Agent → 检索知识库 → 查找相关政策 → 返回证据
   ↓
Report Agent → 整合信息 → 生成报告 → 输出建议
   ↓
返回完整审计结果
```

### 使用 CrewAI 编排（可选）

当 `ENABLE_CREWAI=true` 时，系统使用 CrewAI 框架进行 Agent 编排：

- **优点：** 更智能的任务分配、LLM 驱动的推理、更详细的报告
- **缺点：** 依赖 LLM API、延迟较高、成本较高
- **Fallback：** 如果 CrewAI 失败，自动降级到本地工作流

---

## 设计理念

### 为什么规则优先、模型辅助？

在金融风控领域，**可解释性、确定性和合规性** 至关重要：

#### 1. 确定性保证
- ✅ **规则引擎：** 相同输入永远产生相同输出
- ❌ **纯 LLM：** 存在随机性，难以审计

#### 2. 可解释性
- ✅ **规则引擎：** 每条规则都有明确的业务逻辑
- ❌ **纯 LLM：** 黑盒决策，难以向监管机构解释

#### 3. 合规性
- ✅ **规则引擎：** 符合金融行业监管要求
- ❌ **纯 LLM：** 难以通过合规审计

#### 4. 性能和成本
- ✅ **规则引擎：** 毫秒级响应，零成本
- ❌ **纯 LLM：** 秒级延迟，API 调用费用

### AI Agent 的角色定位

在 PayGuard Crew 中，AI Agent **不做核心决策**，而是：

1. **证据检索** - 从知识库中查找相关政策和规则说明
2. **报告生成** - 将风险评估结果转化为人类可读的文本
3. **建议输出** - 提供操作建议和复核要点
4. **日志记录** - 记录审计过程的每一步

### 架构优势

这种 **规则引擎 + AI Agent** 的混合架构结合了两者的优势：

- **规则引擎** 保证核心风控逻辑的可靠性
- **AI Agent** 提升用户体验和审计效率
- **RAG 检索** 实现知识库的智能利用
- **Multi-Agent** 实现复杂任务的模块化分解

---

## 为什么这是 Demo？

### 不适合生产环境的原因

#### 1. 数据安全
- ❌ 没有加密存储
- ❌ 没有访问控制
- ❌ 没有审计追踪（仅有简单日志）

#### 2. 性能和可扩展性
- ❌ SQLite 不适合高并发
- ❌ 没有缓存机制
- ❌ 没有负载均衡

#### 3. 风控规则
- ❌ 规则过于简化
- ❌ 缺少实时数据源（真实设备指纹、IP 库）
- ❌ 缺少机器学习模型

#### 4. 合规性
- ❌ 缺少完整的 KYC/AML 流程
- ❌ 没有监管报告功能
- ❌ 没有数据留存和审计

### 适合学习和展示

✅ **学习 AI Agent 开发** - 完整的 Multi-Agent 系统示例  
✅ **学习 RAG 应用** - ChromaDB + 知识库检索  
✅ **学习 FastAPI 开发** - RESTful API 最佳实践  
✅ **学习金融风控** - 支付风控业务逻辑  

---

## 测试

### 运行所有测试
```bash
pytest -q
```

### 运行特定测试文件
```bash
pytest tests/test_rules.py -v
pytest tests/test_api.py -v
pytest tests/test_rag.py -v
pytest tests/test_db.py -v
```

### 查看测试覆盖率
```bash
pytest --cov=app --cov-report=html
```

### 测试统计
- **26 个测试** 覆盖规则引擎、API、RAG、数据库
- **100% 通过率**
- 测试用例包括正常流程、边界条件、异常处理

---

## License

MIT License

---

## 致谢

本项目使用了以下优秀的开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [CrewAI](https://www.crewai.com/) - Multi-Agent 编排框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

---

## 联系方式

- GitHub: https://github.com/pocheang
- Email: po.cheang@gmail.com

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**

