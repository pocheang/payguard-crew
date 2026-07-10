# PayGuard 完整启动指南

## 🚀 3种启动方式

### 方式1：快速启动（推荐新手）⭐

**特点**：零配置，使用规则引擎模式

```bash
# 1. 修复依赖问题（首次必须）
./fix-issues.sh  # Linux/Mac
# 或
.\fix-issues.ps1  # Windows

# 2. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 启动前端（新终端）
cd frontend
npm run dev
```

**访问**：
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

**登录**：
- 管理员：`admin` / `admin123`
- 分析师：`demo` / `demo123`

---

### 方式2：Docker启动（推荐生产）⭐⭐

**特点**：一键启动，包含数据库和缓存

```bash
# 使用启动脚本
./start.sh

# 或手动启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

**访问**：
- 前端：http://localhost
- 后端API：http://localhost:8000
- 健康检查：http://localhost:8000/api/health/health

---

### 方式3：开发模式

**特点**：代码热重载，适合开发

```bash
# Docker开发模式
docker-compose -f docker-compose.dev.yml up

# 或手动开发模式
# 终端1：后端
uvicorn app.main:app --reload

# 终端2：前端
cd frontend && npm run dev
```

---

## 📋 启动前检查清单

### 必需项（5分钟）

- [ ] **Node.js已安装**（16+）
  ```bash
  node --version
  ```

- [ ] **Python已安装**（3.11+）
  ```bash
  python --version
  ```

- [ ] **前端依赖已安装**
  ```bash
  cd frontend && npm install
  ```

- [ ] **后端依赖已安装**
  ```bash
  pip install -r requirements.txt
  ```

### 可选项（根据需要）

- [ ] **Docker已安装**（如果使用Docker）
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] **配置.env文件**（使用LLM时）
  ```bash
  cp .env.example .env
  nano .env
  ```

- [ ] **LLM API密钥**（使用AI功能时）
  - OpenAI: https://platform.openai.com/
  - DeepSeek: https://platform.deepseek.com/

---

## 🔧 配置选项

### 最小配置（规则引擎模式）✅

**文件**：`.env`（可选，使用默认值）

```bash
# 应用配置
APP_ENV=dev

# LLM配置 - 禁用（默认）
LLM_PROVIDER=disabled
ENABLE_CREWAI=false

# 其他配置使用默认值
```

> **注意**：规则引擎模式不需要配置LLM，可以直接启动！

---

### 完整配置（AI增强模式）

**文件**：`.env`

```bash
# 应用配置
APP_ENV=dev
APP_NAME=payguard-crew

# 🔒 安全配置（生产环境必须修改）
JWT_SECRET_KEY=your-secret-key-change-in-production
API_KEYS=your-api-key-here

# 🤖 LLM配置（三选一）

# 选项1：DeepSeek（推荐国内）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_MODEL=deepseek-chat
ENABLE_CREWAI=false

# 选项2：OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-openai-key
# OPENAI_MODEL=gpt-4o-mini
# ENABLE_CREWAI=false

# 选项3：本地Ollama
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=qwen2.5
# OLLAMA_BASE_URL=http://localhost:11434/v1
# ENABLE_CREWAI=false

# 📚 RAG配置
RAG_TOP_K=3
PAYGUARD_DOCS_DIR=docs

# 🗄️ 数据库（生产环境）
# DATABASE_URL=postgresql://user:pass@localhost:5432/payguard
# REDIS_URL=redis://localhost:6379/0
```

---

## 🎯 功能模块

### 已实现功能 ✅

#### 1. 认证系统
- [x] JWT Token认证
- [x] 登录/登出
- [x] Token刷新
- [x] 基于角色的权限控制（RBAC）

#### 2. 交易审计
- [x] 单笔交易审计
- [x] 批量交易审计（最多100笔）
- [x] 实时风险评分
- [x] 规则引擎匹配
- [x] 触发规则展示

#### 3. 审核工作流
- [x] 创建审核记录
- [x] 审核状态管理
- [x] 分配审核人
- [x] 添加评论
- [x] 审核统计

#### 4. 报告管理
- [x] 查询历史报告
- [x] 多条件筛选
- [x] CSV导出
- [x] Excel导出
- [x] 分页浏览

#### 5. 数据可视化
- [x] Dashboard统计
- [x] 风险分布图表
- [x] 决策分布图表
- [x] TOP规则展示
- [x] 实时更新

#### 6. UI/UX优化
- [x] 现代化设计系统
- [x] 6个可复用组件
- [x] 响应式布局
- [x] 动画效果
- [x] 暗色主题准备

---

## 🐛 故障排除

### 问题1：前端依赖安装失败

```bash
# 清理重装
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### 问题2：后端无法启动

```bash
# 检查Python版本
python --version  # 需要3.11+

# 重装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 检查端口占用
# Windows
netstat -ano | findstr 8000

# Linux/Mac
lsof -i :8000
```

### 问题3：Docker启动失败

```bash
# 查看日志
docker-compose logs backend
docker-compose logs frontend

# 重新构建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### 问题4：LLM配置错误

```bash
# 检查配置
cat .env | grep LLM

# 使用规则引擎模式（不需要LLM）
echo "LLM_PROVIDER=disabled" >> .env

# 重启服务
```

### 问题5：前端路由404

**原因**：路由配置错误（已修复）

**验证**：检查 `frontend/src/router/index.js` 第2行
```javascript
// 应该是：
import { useAuthStore } from '../stores/auth'
```

---

## 📊 性能优化

### 生产环境建议

1. **使用PostgreSQL代替SQLite**
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost/payguard
   ```

2. **启用Redis缓存**
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

3. **配置Nginx反向代理**
   ```nginx
   location / {
     proxy_pass http://localhost:3000;
   }
   location /api {
     proxy_pass http://localhost:8000;
   }
   ```

4. **使用Docker部署**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目总览 |
| [ISSUES_REPORT.md](ISSUES_REPORT.md) | 问题检查报告 |
| [LLM_CONFIG_GUIDE.md](LLM_CONFIG_GUIDE.md) | LLM模型配置 |
| [DOCKER.md](DOCKER.md) | Docker部署指南 |
| [frontend/DESIGN_SYSTEM.md](frontend/DESIGN_SYSTEM.md) | 前端设计系统 |
| [frontend/README.md](frontend/README.md) | 前端文档 |
| [frontend/QUICKSTART.md](frontend/QUICKSTART.md) | 前端快速开始 |

---

## 🎯 Demo演示流程

### 1. 登录系统（30秒）
1. 访问 http://localhost:3000
2. 点击"管理员"快速填充
3. 点击"登录"

### 2. 查看Dashboard（1分钟）
- 总交易数统计
- 风险等级分布
- 图表可视化
- 最近审计记录

### 3. 单笔交易审计（2分钟）
1. 点击"单笔审计"
2. 点击"高风险场景"
3. 点击"开始审计"
4. 查看风险评估结果

### 4. 批量审计（2分钟）
1. 点击"批量审计"
2. 点击"添加 20 笔样例"
3. 点击"批量审计"
4. 查看批量结果

### 5. 审核工作流（2分钟）
1. 点击"待审核"
2. 点击某个交易"查看详情"
3. 输入审核意见
4. 点击"批准"或"拒绝"

### 6. 报告导出（1分钟）
1. 点击"报告查询"
2. 勾选几条记录
3. 点击"导出CSV"

**总计：8-10分钟完整演示**

---

## ✅ 成功启动标志

### 后端启动成功
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 前端启动成功
```
VITE v5.1.5  ready in 1234 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 健康检查通过
```bash
curl http://localhost:8000/api/health/health

# 返回：
{
  "status": "ok",
  "version": "0.2.0",
  "timestamp": "2026-07-09T...",
  "components": {...}
}
```

---

## 🎉 快速启动命令

```bash
# 一键修复并查看指南
./fix-issues.sh && cat STARTUP_GUIDE.md

# 启动后端
uvicorn app.main:app --reload

# 启动前端（新终端）
cd frontend && npm run dev

# 或使用Docker
./start.sh
```

**🚀 现在就可以开始使用PayGuard了！**
