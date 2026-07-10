# PayGuard - 企业级支付风控系统

<div align="center">

![PayGuard Logo](https://img.shields.io/badge/PayGuard-v0.2.0-blue)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.4+-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-blue.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**基于AI的智能支付风险控制平台**

[快速开始](#-快速开始) •
[文档](#-文档) •
[功能特性](#-功能特性) •
[演示](#-演示) •
[贡献指南](CONTRIBUTING.md)

</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [项目架构](#-项目架构)
- [技术栈](#-技术栈)
- [文档](#-文档)
- [性能指标](#-性能指标)
- [安全特性](#-安全特性)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## ✨ 功能特性

### 核心功能

- 🚀 **实时风控** - 毫秒级交易风险评估
- 🤖 **AI增强** - 支持OpenAI、DeepSeek、Ollama多种LLM
- 📊 **可视化Dashboard** - 实时监控和数据分析
- 🔄 **批量处理** - 最多100笔交易并发审计
- 👥 **审核工作流** - 完整的人工复核流程
- 📈 **数据导出** - CSV/Excel报告导出
- 🐳 **Docker部署** - 一键启动，生产就绪
- 🎨 **现代UI** - Vue 3 + Tailwind CSS

### 技术亮点

- ✅ **企业级安全** - 多层防护、输入验证、SQL注入防护
- ✅ **高性能优化** - 前端98.6%体积优化、Redis缓存
- ✅ **测试完善** - 60%+测试覆盖率
- ✅ **文档齐全** - 完整的技术文档和API文档
- ✅ **易于扩展** - 清晰的模块化架构

---

## 🚀 快速开始

### 方式1：一键Docker部署（推荐）

```bash
# Windows
.\deploy.ps1

# Linux/Mac
chmod +x deploy.sh
./deploy.sh
```

选择部署模式后，访问：
- 前端：http://localhost:3000
- 后端：http://localhost:8000
- API文档：http://localhost:8000/docs

### 方式2：本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/payguard.git
cd payguard

# 2. 配置环境
cp .env.example .env
# 编辑 .env 配置必要参数

# 3. 启动后端
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. 启动前端（新终端）
cd frontend
npm install
npm run dev
```

### 默认登录凭据

```
管理员: admin / admin123
演示账号: demo / demo123
```

> ⚠️ **生产环境必须修改默认密码！**

---

## 🏗️ 项目架构

```
payguard/
├── app/                    # 后端应用
│   ├── api/               # API路由层
│   ├── core/              # 核心功能
│   ├── services/          # 业务逻辑层
│   ├── db/                # 数据访问层
│   ├── auth/              # 认证授权
│   └── rules/             # 规则引擎
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   ├── views/        # 页面视图
│   │   ├── stores/       # 状态管理
│   │   └── router/       # 路由配置
├── tests/                 # 测试套件
├── docs/                  # 文档中心
└── scripts/               # 工具脚本
```

详细架构说明：[架构文档](docs/architecture/SYSTEM_COMPLETE.md)

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 主语言 |
| FastAPI | 0.115+ | Web框架 |
| Pydantic | 2.x | 数据验证 |
| SQLAlchemy | 2.x | ORM |
| PostgreSQL | 13+ | 数据库（生产） |
| Redis | 6+ | 缓存（生产） |
| SQLite | 3.x | 数据库（开发） |

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.4+ | 前端框架 |
| Vite | 5.x | 构建工具 |
| Pinia | 2.x | 状态管理 |
| Tailwind CSS | 3.x | CSS框架 |
| ECharts | 5.x | 图表库 |

### AI/LLM

- OpenAI GPT系列
- DeepSeek（国内推荐）
- Ollama（本地部署）
- CrewAI（多Agent协作）

---

## 📚 文档

### 快速导航

| 文档 | 说明 |
|------|------|
| [快速开始](docs/guides/QUICK_START.md) | 5分钟上手指南 |
| [快速参考](docs/guides/QUICK_REFERENCE.md) | 常用操作速查 |
| [部署指南](docs/guides/DOCKER_DEPLOYMENT.md) | Docker部署详解 |
| [API文档](docs/api/API_DOCUMENTATION.md) | 完整API参考 |
| [代码组织](docs/guides/CODE_ORGANIZATION_GUIDE.md) | 代码规范指南 |

### 技术报告

| 文档 | 说明 |
|------|------|
| [代码审查报告](docs/reports/CODE_REVIEW_REPORT.md) | 代码质量分析 |
| [性能优化报告](docs/reports/PERFORMANCE_OPTIMIZATION_REPORT.md) | 性能优化详情 |
| [修复完成报告](docs/reports/FIXES_COMPLETED.md) | 所有修复内容 |

### 完整文档索引

查看 [文档中心](docs/README.md) 获取所有文档列表。

---

## 📈 性能指标

### 前端性能

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| Dashboard体积 | 1050 KB | **15 KB** | **-98.6%** |
| 构建时间 | 8.12s | **6.18s** | **-24%** |
| 首屏加载 | ~1.2MB | **~110KB** | **-91%** |

### 系统性能

- ⚡ 响应时间: < 100ms（规则引擎模式）
- 🚀 吞吐量: 1000+ TPS（单机）
- 💾 内存占用: < 512MB（后端）
- ⏱️ 启动时间: < 30s（开发）

---

## 🔒 安全特性

- ✅ **多层防护** - API Key + JWT认证
- ✅ **输入验证** - Pydantic模型验证 + 自定义验证
- ✅ **SQL注入防护** - 参数化查询 + 输入清洗
- ✅ **XSS防护** - 输出转义 + CSP策略
- ✅ **CORS配置** - 严格的跨域控制
- ✅ **速率限制** - Slowapi + Redis
- ✅ **审计日志** - 完整的操作记录
- ✅ **密钥管理** - 环境变量 + 强度验证

详细安全说明：[安全文档](docs/guides/SECURITY.md)

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/api/test_audit.py -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 测试覆盖

- 单元测试：60%+
- API测试：完整覆盖核心接口
- 集成测试：主要业务流程

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循 [代码组织指南](docs/guides/CODE_ORGANIZATION_GUIDE.md)
- 添加单元测试
- 更新相关文档
- 确保所有测试通过

详细说明：[贡献指南](CONTRIBUTING.md)

---

## 📊 项目状态

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/payguard)
![GitHub issues](https://img.shields.io/github/issues/yourusername/payguard)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/payguard)

### 版本历史

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本变更。

### 路线图

- [x] v0.1.0 - 基础风控功能
- [x] v0.2.0 - Docker部署 + 前端优化
- [ ] v0.3.0 - WebSocket实时通知
- [ ] v0.4.0 - Kubernetes支持
- [ ] v1.0.0 - 生产就绪

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [ECharts](https://echarts.apache.org/)
- [CrewAI](https://www.crewai.com/)

---

## 📄 许可证

本项目采用 MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- 📧 Email: support@payguard.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/payguard/issues)
- 📖 文档: [完整文档](docs/README.md)

---

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个Star！

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/payguard&type=Date)](https://star-history.com/#yourusername/payguard&Date)

---

<div align="center">

**🎉 PayGuard - 让支付更安全 🎉**

Made with ❤️ by PayGuard Team

[官网](https://payguard.com) · [文档](https://docs.payguard.com) · [博客](https://blog.payguard.com)

</div>
