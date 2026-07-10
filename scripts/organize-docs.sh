#!/bin/bash
# 文档整理脚本 - 将混乱的根目录文档整理到 docs/ 目录

set -e

echo "================================"
echo "文档整理脚本"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 创建目录结构
echo -e "${YELLOW}创建目录结构...${NC}"
mkdir -p docs/{reports,guides,architecture,api,archive}
echo -e "${GREEN}✓ 目录创建完成${NC}"
echo ""

echo -e "${YELLOW}整理文档到对应目录...${NC}"
echo ""

# 报告类 -> docs/reports/
for file in CODE_REVIEW_REPORT.md PERFORMANCE_OPTIMIZATION_REPORT.md \
            FIXES_COMPLETED.md FINAL_SUMMARY.md PROJECT_STATUS.md \
            PROJECT_FINAL_SUMMARY.md COMPLETION_SUMMARY.md P1_TASKS_COMPLETE.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/reports/
        echo -e "  ${GREEN}✓${NC} $file -> docs/reports/"
    fi
done

# 指南类 -> docs/guides/
for file in QUICK_START.md QUICK_REFERENCE.md FIX_IMPLEMENTATION_GUIDE.md \
            CODE_ORGANIZATION_GUIDE.md STARTUP_GUIDE.md DEPLOYMENT_GUIDE.md \
            DOCKER_DEPLOYMENT.md DOCKER_GUIDE.md DOCKER_DEV_GUIDE.md \
            LLM_CONFIG_GUIDE.md ENVIRONMENT_GUIDE.md GITHUB_GUIDE.md \
            GIT_COMMIT_GUIDE.md ONE_CLICK_DEPLOY.md DEMO_GUIDE.md \
            HOW_TO_DEMO.md DEMO_INSTRUCTIONS.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/guides/
        echo -e "  ${GREEN}✓${NC} $file -> docs/guides/"
    fi
done

# API文档 -> docs/api/
for file in API_DOCUMENTATION.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/api/
        echo -e "  ${GREEN}✓${NC} $file -> docs/api/"
    fi
done

# 架构文档 -> docs/architecture/
for file in SYSTEM_COMPLETE.md FRONTEND_COMPLETION.md \
            FRONTEND_VISUALIZATION.md REVIEW_ENHANCEMENTS.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/architecture/
        echo -e "  ${GREEN}✓${NC} $file -> docs/architecture/"
    fi
done

# 归档过期文档 -> docs/archive/
for file in COMPLETION_PLAN.md DEMO_STATUS.md ENVIRONMENT_SUMMARY.md \
            FUNCTION_CHECK_REPORT.md FRONTEND_DOCKER_IMPROVEMENTS.md \
            PERFORMANCE_OPTIMIZATION.md START_HERE.md README_DOCKER.md DOCKER.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/archive/
        echo -e "  ${YELLOW}✓${NC} $file -> docs/archive/ (归档)"
    fi
done

echo ""
echo -e "${YELLOW}创建文档索引...${NC}"

# 创建 docs/README.md 索引
cat > docs/README.md << 'EOF'
# PayGuard 文档中心

> **项目**: PayGuard Crew Starter v0.2.0
> **更新**: 2026-07-10

---

## 📚 文档导航

### 🚀 快速开始

| 文档 | 说明 |
|------|------|
| [../README.md](../README.md) | 项目主文档 |
| [QUICK_START.md](guides/QUICK_START.md) | 快速启动指南 |
| [QUICK_REFERENCE.md](guides/QUICK_REFERENCE.md) | 快速参考 |

### 📋 技术报告

| 文档 | 说明 |
|------|------|
| [CODE_REVIEW_REPORT.md](reports/CODE_REVIEW_REPORT.md) | 代码审查报告 |
| [PERFORMANCE_OPTIMIZATION_REPORT.md](reports/PERFORMANCE_OPTIMIZATION_REPORT.md) | 性能优化报告 |
| [FIXES_COMPLETED.md](reports/FIXES_COMPLETED.md) | 修复完成报告 |
| [FINAL_SUMMARY.md](reports/FINAL_SUMMARY.md) | 最终总结 |

### 📖 使用指南

| 文档 | 说明 |
|------|------|
| [DEPLOYMENT_GUIDE.md](guides/DEPLOYMENT_GUIDE.md) | 部署指南 |
| [DOCKER_DEPLOYMENT.md](guides/DOCKER_DEPLOYMENT.md) | Docker部署 |
| [LLM_CONFIG_GUIDE.md](guides/LLM_CONFIG_GUIDE.md) | LLM配置 |
| [FIX_IMPLEMENTATION_GUIDE.md](guides/FIX_IMPLEMENTATION_GUIDE.md) | 修复实施指南 |
| [CODE_ORGANIZATION_GUIDE.md](../CODE_ORGANIZATION_GUIDE.md) | 代码组织指南 |

### 🏗️ 架构文档

| 文档 | 说明 |
|------|------|
| [SYSTEM_COMPLETE.md](architecture/SYSTEM_COMPLETE.md) | 系统架构 |
| [FRONTEND_COMPLETION.md](architecture/FRONTEND_COMPLETION.md) | 前端架构 |

### 🔌 API文档

| 文档 | 说明 |
|------|------|
| [API_DOCUMENTATION.md](api/API_DOCUMENTATION.md) | API接口文档 |

---

## 📂 目录结构

```
docs/
├── README.md           # 本文件（文档索引）
├── reports/            # 技术报告
├── guides/             # 使用指南
├── architecture/       # 架构文档
├── api/                # API文档
└── archive/            # 归档文档
```

---

**更新时间**: 2026-07-10
EOF

echo -e "${GREEN}  ✓ 创建 docs/README.md${NC}"

echo ""
echo "================================"
echo -e "${GREEN}✓ 文档整理完成！${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}整理结果:${NC}"
echo -e "  ${CYAN}- 报告文档: docs/reports/${NC}"
echo -e "  ${CYAN}- 使用指南: docs/guides/${NC}"
echo -e "  ${CYAN}- 架构文档: docs/architecture/${NC}"
echo -e "  ${CYAN}- API文档: docs/api/${NC}"
echo -e "  ${CYAN}- 归档文档: docs/archive/${NC}"
echo ""
echo -e "${YELLOW}查看文档索引: docs/README.md${NC}"
