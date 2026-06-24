# PayGuard Crew 文档索引

**版本**: 0.1.0  
**更新日期**: 2026-06-24

---

## 📚 核心文档

### 1. [README.md](README.md)
**主要项目文档** - 完整的项目介绍、安装指南、使用说明

- 项目介绍和定位
- 系统架构设计
- 技术栈说明
- 核心功能介绍
- 快速开始指南
- Docker 部署说明
- API 使用示例
- 风控规则说明
- Agent 职责说明
- 设计理念
- 扩展方向
- 简历项目描述

### 2. [PAYGUARD_CREW_DEV.md](PAYGUARD_CREW_DEV.md)
**开发设计文档** - 系统设计、架构、开发指南

- 项目定位
- 技术栈
- 系统架构
- Agent 设计
- 数据字段设计
- 风控规则设计
- API 设计
- 开发阶段说明

### 3. [CHANGELOG.md](CHANGELOG.md)
**变更日志** - 版本历史和更新记录

- 版本 0.1.0 的新增功能
- 核心功能列表
- 版本说明

---

## 📖 业务文档（知识库）

位于 `docs/` 目录，用于 RAG 检索：

### 1. [docs/kyc_policy.md](docs/kyc_policy.md)
KYC（Know Your Customer）身份认证政策

### 2. [docs/aml_review_guide.md](docs/aml_review_guide.md)
AML（Anti-Money Laundering）反洗钱审核指南

### 3. [docs/payment_risk_rules.md](docs/payment_risk_rules.md)
支付风险规则说明

### 4. [docs/merchant_risk_policy.md](docs/merchant_risk_policy.md)
商户风险管理政策

### 5. [docs/manual_review_process.md](docs/manual_review_process.md)
人工复核流程说明

### 6. [docs/api_documentation.md](docs/api_documentation.md)
API 接口详细文档

---

## 🚀 快速导航

### 新手入门
1. 阅读 [README.md](README.md) 了解项目
2. 按照"快速开始"章节安装和配置
3. 运行示例测试 API

### 开发者
1. 阅读 [PAYGUARD_CREW_DEV.md](PAYGUARD_CREW_DEV.md) 了解架构
2. 查看 `app/` 目录下的代码
3. 运行测试：`pytest tests/ -v`

### 业务理解
1. 阅读 `docs/` 目录下的业务文档
2. 了解风控规则和合规流程
3. 测试不同的交易场景

---

## 📁 项目结构

```
payguard_crew_starter/
├── README.md                    # 主文档
├── PAYGUARD_CREW_DEV.md        # 开发设计文档
├── CHANGELOG.md                 # 变更日志
├── VERSION.txt                  # 版本号
├── DOCS_INDEX.md               # 本文档
├── app/                         # 应用代码
│   ├── agents/                  # AI Agent 定义
│   ├── api/                     # FastAPI 路由
│   ├── crew/                    # CrewAI 编排
│   ├── db/                      # 数据库
│   ├── rag/                     # RAG 检索
│   ├── rules/                   # 风控规则
│   ├── schemas/                 # 数据模型
│   ├── middleware/              # 中间件
│   ├── auth/                    # 认证
│   ├── utils/                   # 工具函数
│   ├── config.py                # 配置管理
│   └── main.py                  # 应用入口
├── docs/                        # 业务文档（知识库）
│   ├── kyc_policy.md
│   ├── aml_review_guide.md
│   ├── payment_risk_rules.md
│   ├── merchant_risk_policy.md
│   ├── manual_review_process.md
│   └── api_documentation.md
├── tests/                       # 测试套件
├── scripts/                     # 脚本
├── data/                        # 示例数据
├── requirements.txt             # 依赖
├── requirements-dev.txt         # 开发依赖
├── pyproject.toml              # 工具配置
├── Dockerfile                   # Docker 配置
└── docker-compose.yml          # Docker Compose

```

---

## 🔧 配置文件

- `.env` - 环境变量配置（需要从 `.env.example` 复制）
- `pyproject.toml` - 代码质量工具配置
- `pytest.ini` - Pytest 配置
- `requirements.txt` - Python 依赖
- `requirements-dev.txt` - 开发工具依赖

---

## 📊 版本信息

**当前版本**: 0.1.0  
**发布日期**: 2026-06-24

### 版本 0.1.0 主要功能

- ✅ 7 大风控规则引擎（R001-R007）
- ✅ Multi-Agent 协作架构
- ✅ RAG 知识库检索
- ✅ FastAPI RESTful API
- ✅ SQLite 数据持久化
- ✅ CrewAI 可选编排
- ✅ Docker 容器化部署
- ✅ 完整的测试套件

---

## 🎯 文档使用建议

### 场景 1: 首次接触项目
**阅读顺序**: README.md → 快速开始 → API 测试

### 场景 2: 深入理解架构
**阅读顺序**: PAYGUARD_CREW_DEV.md → 代码结构 → 业务文档

### 场景 3: 准备面试/简历
**重点阅读**: README.md 中的"简历项目描述"和"面试话术"

### 场景 4: 扩展开发
**参考文档**: PAYGUARD_CREW_DEV.md + 代码注释 + API 文档

---

## 📝 贡献指南

如需添加或修改文档：

1. 更新对应的文档文件
2. 更新本索引文件
3. 更新 CHANGELOG.md
4. 提交 Pull Request

---

## 📞 联系与支持

- **GitHub**: [您的 GitHub]
- **Email**: [您的邮箱]
- **问题反馈**: 在 GitHub Issues 中提交

---

**最后更新**: 2026-06-24  
**维护者**: PayGuard Crew Team
