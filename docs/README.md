# PayGuard 文档中心

> **项目**: PayGuard v0.2.0  
> **更新**: 2026-07-10

---

## 📚 快速导航

### 🚀 新手入门

| 文档 | 说明 | 预计时间 |
|------|------|---------|
| [项目主页](../README.md) | 项目概述和功能介绍 | 5分钟 |
| [快速开始](guides/QUICK_START.md) | 5分钟上手指南 | 5分钟 |
| [快速参考](guides/QUICK_REFERENCE.md) | 常用命令速查 | 2分钟 |
| [演示指南](guides/DEMO.md) | 完整演示流程 | 15分钟 |

### 📦 部署指南

| 文档 | 说明 |
|------|------|
| [Docker部署](guides/DOCKER.md) | Docker完整部署指南（推荐） |
| [环境配置](guides/ENVIRONMENT_GUIDE.md) | 环境变量配置说明 |
| [启动指南](guides/STARTUP_GUIDE.md) | 手动启动步骤 |
| [故障排除](guides/TROUBLESHOOTING.md) | 常见问题解决 |
| [一键部署](guides/ONE_CLICK_DEPLOY.md) | 自动化部署脚本 |

### 🔌 API文档

| 文档 | 说明 |
|------|------|
| [API完整文档](api/API_DOCUMENTATION.md) | 所有API接口详细说明 |
| 在线API文档 | 启动后访问 http://localhost:8000/docs |

### 🏗️ 架构设计

| 文档 | 说明 |
|------|------|
| [系统架构](architecture/SYSTEM_COMPLETE.md) | 完整系统架构说明 |
| [前端架构](architecture/FRONTEND_COMPLETION.md) | 前端技术架构 |
| [前端可视化](architecture/FRONTEND_VISUALIZATION.md) | 图表和可视化设计 |
| [审核增强](architecture/REVIEW_ENHANCEMENTS.md) | 审核工作流设计 |

### 📖 开发指南

| 文档 | 说明 |
|------|------|
| [代码组织](guides/CODE_ORGANIZATION_GUIDE.md) | 代码结构和规范 |
| [贡献指南](../CONTRIBUTING.md) | 如何参与贡献 |
| [LLM配置](guides/LLM_CONFIG_GUIDE.md) | AI模型配置指南 |
| [批量功能](guides/BATCH_FEATURES.md) | 批量处理功能说明 |
| [审核工作流](guides/REVIEW_WORKFLOW.md) | 审核流程说明 |

### 📋 业务规则

| 文档 | 说明 |
|------|------|
| [支付风险规则](guides/payment_risk_rules.md) | 支付风险规则配置 |
| [KYC政策](guides/kyc_policy.md) | 客户身份验证政策 |
| [商户风险政策](guides/merchant_risk_policy.md) | 商户风险管理 |
| [AML审核指南](guides/aml_review_guide.md) | 反洗钱审核流程 |
| [人工审核流程](guides/manual_review_process.md) | 人工审核标准 |

### 📊 技术报告

| 文档 | 说明 |
|------|------|
| [项目综合报告](reports/PROJECT_SUMMARY.md) | ⭐ 完整项目总结 |
| [代码审查报告](reports/CODE_REVIEW_REPORT.md) | 代码质量分析 |
| [性能优化报告](reports/PERFORMANCE_OPTIMIZATION_REPORT.md) | 性能优化详情 |
| [修复完成报告](reports/FIXES_COMPLETED.md) | Bug修复记录 |
| [安全审计报告](reports/SECURITY_AUDIT_REPORT.md) | 安全性分析 |
| [企业架构](reports/ENTERPRISE_ARCHITECTURE.md) | 企业级架构设计 |

### 🔧 工具和脚本

| 文档 | 说明 |
|------|------|
| [GitHub指南](guides/GITHUB_GUIDE.md) | GitHub工作流程 |
| [Git提交规范](guides/GIT_COMMIT_GUIDE.md) | 提交消息规范 |
| [重构指南](guides/REFACTORING_GUIDE.md) | 代码重构指南 |
| [修复实施指南](guides/FIX_IMPLEMENTATION_GUIDE.md) | Bug修复流程 |

---

## 📂 文档结构

```
docs/
├── README.md                           # 本文档
│
├── api/                                # API文档
│   └── API_DOCUMENTATION.md           # 完整API参考
│
├── guides/                             # 使用指南
│   ├── QUICK_START.md                 # 快速开始
│   ├── DOCKER.md                      # Docker部署（合并）
│   ├── DEMO.md                        # 演示指南（合并）
│   ├── ENVIRONMENT_GUIDE.md           # 环境配置
│   ├── CODE_ORGANIZATION_GUIDE.md     # 代码组织
│   ├── LLM_CONFIG_GUIDE.md            # LLM配置
│   ├── BATCH_FEATURES.md              # 批量功能
│   ├── REVIEW_WORKFLOW.md             # 审核工作流
│   ├── TROUBLESHOOTING.md             # 故障排除
│   ├── payment_risk_rules.md          # 支付风险规则
│   ├── kyc_policy.md                  # KYC政策
│   ├── merchant_risk_policy.md        # 商户风险政策
│   ├── aml_review_guide.md            # AML审核指南
│   └── manual_review_process.md       # 人工审核流程
│
├── architecture/                       # 架构文档
│   ├── SYSTEM_COMPLETE.md             # 系统架构
│   ├── FRONTEND_COMPLETION.md         # 前端架构
│   ├── FRONTEND_VISUALIZATION.md      # 前端可视化
│   └── REVIEW_ENHANCEMENTS.md         # 审核增强
│
├── reports/                            # 技术报告
│   ├── PROJECT_SUMMARY.md             # ⭐ 项目综合报告
│   ├── CODE_REVIEW_REPORT.md          # 代码审查
│   ├── PERFORMANCE_OPTIMIZATION_REPORT.md  # 性能优化
│   ├── FIXES_COMPLETED.md             # 修复完成
│   ├── SECURITY_AUDIT_REPORT.md       # 安全审计
│   ├── ENTERPRISE_ARCHITECTURE.md     # 企业架构
│   ├── ENTERPRISE_FEATURES.md         # 企业功能
│   └── ...                            # 其他报告
│
└── archive/                            # 历史文档
    ├── COMPLETION_PLAN.md             # 完成计划
    ├── DEMO_STATUS.md                 # 演示状态
    ├── ENVIRONMENT_SUMMARY.md         # 环境总结
    └── ...                            # 其他历史文档
```

---

## 🎯 推荐阅读路径

### 路径1: 快速上手（30分钟）

1. 阅读 [README.md](../README.md) - 了解项目
2. 按照 [快速开始](guides/QUICK_START.md) - 启动系统
3. 参考 [演示指南](guides/DEMO.md) - 体验功能
4. 查看 [API文档](api/API_DOCUMENTATION.md) - 了解接口

### 路径2: 开发者深入（2小时）

1. [代码组织指南](guides/CODE_ORGANIZATION_GUIDE.md) - 理解架构
2. [系统架构](architecture/SYSTEM_COMPLETE.md) - 深入设计
3. [贡献指南](../CONTRIBUTING.md) - 参与开发
4. [代码审查报告](reports/CODE_REVIEW_REPORT.md) - 了解质量

### 路径3: 运维部署（1小时）

1. [Docker部署](guides/DOCKER.md) - 部署方案
2. [环境配置](guides/ENVIRONMENT_GUIDE.md) - 配置详解
3. [故障排除](guides/TROUBLESHOOTING.md) - 问题解决
4. [性能优化报告](reports/PERFORMANCE_OPTIMIZATION_REPORT.md) - 优化建议

### 路径4: 业务使用（1小时）

1. [演示指南](guides/DEMO.md) - 功能演示
2. [审核工作流](guides/REVIEW_WORKFLOW.md) - 业务流程
3. [支付风险规则](guides/payment_risk_rules.md) - 规则说明
4. [人工审核流程](guides/manual_review_process.md) - 操作指南

---

## 🔍 按主题查找

### 安装和部署
- [快速开始](guides/QUICK_START.md)
- [Docker部署](guides/DOCKER.md)
- [环境配置](guides/ENVIRONMENT_GUIDE.md)
- [一键部署](guides/ONE_CLICK_DEPLOY.md)

### API和集成
- [API文档](api/API_DOCUMENTATION.md)
- [LLM配置](guides/LLM_CONFIG_GUIDE.md)
- [批量功能](guides/BATCH_FEATURES.md)

### 开发和维护
- [代码组织](guides/CODE_ORGANIZATION_GUIDE.md)
- [贡献指南](../CONTRIBUTING.md)
- [Git规范](guides/GIT_COMMIT_GUIDE.md)
- [重构指南](guides/REFACTORING_GUIDE.md)

### 业务和规则
- [支付风险规则](guides/payment_risk_rules.md)
- [审核工作流](guides/REVIEW_WORKFLOW.md)
- [KYC政策](guides/kyc_policy.md)
- [商户风险政策](guides/merchant_risk_policy.md)

### 故障和优化
- [故障排除](guides/TROUBLESHOOTING.md)
- [性能优化](reports/PERFORMANCE_OPTIMIZATION_REPORT.md)
- [安全审计](reports/SECURITY_AUDIT_REPORT.md)

---

## 📝 文档贡献

文档和代码同样重要！

### 如何改进文档

1. Fork项目
2. 编辑或创建Markdown文件
3. 提交Pull Request
4. 等待审查和合并

### 文档规范

- 使用清晰的标题层次
- 提供代码示例
- 包含目录和导航
- 保持格式一致
- 定期更新日期

详见 [贡献指南](../CONTRIBUTING.md)

---

## 🔗 外部资源

### 官方资源
- 项目主页: https://github.com/yourusername/payguard
- 在线文档: https://docs.payguard.com
- 问题反馈: https://github.com/yourusername/payguard/issues

### 技术文档
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Vue.js文档](https://vuejs.org/)
- [Docker文档](https://docs.docker.com/)
- [ECharts文档](https://echarts.apache.org/)

### 相关项目
- [CrewAI](https://www.crewai.com/)
- [LangChain](https://www.langchain.com/)
- [OpenAI](https://openai.com/)

---

## 📞 获取帮助

遇到问题？这里有几种方式获得帮助：

1. **查看文档** - 大多数问题在文档中都有答案
2. **搜索Issues** - 可能其他人遇到过同样的问题
3. **提问** - 在GitHub Issues中提问
4. **联系我们** - support@payguard.com

---

## 🎉 文档更新日志

### v0.2.0 (2026-07-10)
- ✅ 重组文档结构（39个文件 → 结构化）
- ✅ 合并Docker文档（3个 → 1个）
- ✅ 合并Demo文档（3个 → 1个）
- ✅ 创建项目综合报告
- ✅ 更新所有文档索引
- ✅ 添加推荐阅读路径

### v0.1.0 (2026-07-09)
- ✅ 初始文档集合
- ✅ API文档
- ✅ 快速开始指南
- ✅ Docker部署指南

---

**文档维护**: PayGuard Team  
**最后更新**: 2026-07-10  
**下次审查**: v0.3.0 发布时

---

<div align="center">

**📚 让文档更好，让开发更简单 📚**

[返回顶部](#payguard-文档中心)

</div>
