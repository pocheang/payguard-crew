# 变更日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 添加全局异常处理器
- 添加配置启动验证
- 添加结构化日志工具 (app/utils/logger.py)
- 添加开发依赖配置 (requirements-dev.txt)
- 添加代码格式化配置 (pyproject.toml)
- 添加快速优化脚本 (scripts/quick-fix.sh, scripts/quick-fix.ps1)
- 添加 .gitignore 完善版本控制

### 优化
- 优化错误提示信息的可读性
- 优化配置验证逻辑
- 完善文档 (CODE_REVIEW.md, OPTIMIZATION_CHECKLIST.md)

## [0.1.0] - 2026-06-24

### 新增
- 初始版本发布
- 7 大风控规则引擎 (R001-R007)
- Multi-Agent 协作架构（Transaction、Evidence、Report Agent）
- RAG 知识库检索（ChromaDB + Fallback）
- FastAPI RESTful API
- SQLite 数据持久化
- CrewAI 可选编排
- Docker 容器化部署
- 26 个测试用例
- 完整的 README 和开发文档

### 核心功能
- 交易风险评估
- 合规审核（KYC/AML）
- 黑名单筛查
- 风险评分与分级
- 审核报告生成
- 审计日志记录

---

## 版本说明

### [未发布]
正在开发中的功能和修复

### [0.1.0] - 2026-06-24
首个公开发布版本
