# 文档整理脚本 (Windows PowerShell)
# 将混乱的根目录文档整理到 docs/ 目录

Write-Host "================================" -ForegroundColor Cyan
Write-Host "文档整理脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 创建目录结构
$dirs = @(
    "docs/reports",
    "docs/guides",
    "docs/architecture",
    "docs/api",
    "docs/archive"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ 创建目录: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "整理文档到对应目录..." -ForegroundColor Yellow
Write-Host ""

# 报告类 -> docs/reports/
$reports = @(
    "CODE_REVIEW_REPORT.md",
    "PERFORMANCE_OPTIMIZATION_REPORT.md",
    "FIXES_COMPLETED.md",
    "FINAL_SUMMARY.md",
    "PROJECT_STATUS.md",
    "PROJECT_FINAL_SUMMARY.md",
    "COMPLETION_SUMMARY.md",
    "P1_TASKS_COMPLETE.md"
)

foreach ($file in $reports) {
    if (Test-Path $file) {
        Move-Item $file "docs/reports/" -Force
        Write-Host "  ✓ $file -> docs/reports/" -ForegroundColor Green
    }
}

# 指南类 -> docs/guides/
$guides = @(
    "QUICK_START.md",
    "QUICK_REFERENCE.md",
    "FIX_IMPLEMENTATION_GUIDE.md",
    "CODE_ORGANIZATION_GUIDE.md",
    "STARTUP_GUIDE.md",
    "DEPLOYMENT_GUIDE.md" ,
    "DOCKER_DEPLOYMENT.md",
    "DOCKER_GUIDE.md",
    "DOCKER_DEV_GUIDE.md",
    "LLM_CONFIG_GUIDE.md",
    "ENVIRONMENT_GUIDE.md",
    "GITHUB_GUIDE.md",
    "GIT_COMMIT_GUIDE.md",
    "ONE_CLICK_DEPLOY.md",
    "DEMO_GUIDE.md",
    "HOW_TO_DEMO.md",
    "DEMO_INSTRUCTIONS.md"
)

foreach ($file in $guides) {
    if (Test-Path $file) {
        Move-Item $file "docs/guides/" -Force
        Write-Host "  ✓ $file -> docs/guides/" -ForegroundColor Green
    }
}

# API文档 -> docs/api/
$api_docs = @(
    "API_DOCUMENTATION.md"
)

foreach ($file in $api_docs) {
    if (Test-Path $file) {
        Move-Item $file "docs/api/" -Force
        Write-Host "  ✓ $file -> docs/api/" -ForegroundColor Green
    }
}

# 架构文档 -> docs/architecture/
$arch_docs = @(
    "SYSTEM_COMPLETE.md",
    "FRONTEND_COMPLETION.md",
    "FRONTEND_VISUALIZATION.md",
    "REVIEW_ENHANCEMENTS.md"
)

foreach ($file in $arch_docs) {
    if (Test-Path $file) {
        Move-Item $file "docs/architecture/" -Force
        Write-Host "  ✓ $file -> docs/architecture/" -ForegroundColor Green
    }
}

# 归档过期文档 -> docs/archive/
$archive_docs = @(
    "COMPLETION_PLAN.md",
    "DEMO_STATUS.md",
    "ENVIRONMENT_SUMMARY.md",
    "FUNCTION_CHECK_REPORT.md",
    "FRONTEND_DOCKER_IMPROVEMENTS.md",
    "PERFORMANCE_OPTIMIZATION.md",
    "START_HERE.md",
    "README_DOCKER.md",
    "DOCKER.md"
)

foreach ($file in $archive_docs) {
    if (Test-Path $file) {
        Move-Item $file "docs/archive/" -Force
        Write-Host "  ✓ $file -> docs/archive/ (归档)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "创建文档索引..." -ForegroundColor Yellow

# 创建 docs/README.md 索引
$index = @"
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

``````
docs/
├── README.md           # 本文件（文档索引）
├── reports/            # 技术报告
├── guides/             # 使用指南
├── architecture/       # 架构文档
├── api/                # API文档
└── archive/            # 归档文档
``````

---

**更新时间**: 2026-07-10
"@

$index | Out-File -FilePath "docs/README.md" -Encoding UTF8
Write-Host "  ✓ 创建 docs/README.md" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✓ 文档整理完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "整理结果:" -ForegroundColor Yellow
Write-Host "  - 报告文档: docs/reports/" -ForegroundColor Cyan
Write-Host "  - 使用指南: docs/guides/" -ForegroundColor Cyan
Write-Host "  - 架构文档: docs/architecture/" -ForegroundColor Cyan
Write-Host "  - API文档: docs/api/" -ForegroundColor Cyan
Write-Host "  - 归档文档: docs/archive/" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看文档索引: docs/README.md" -ForegroundColor Yellow
