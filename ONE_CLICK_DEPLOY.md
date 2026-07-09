# PayGuard 一键部署指南

## 🚀 超简单！3步完成部署

### Windows 用户

```powershell
# 1. 进入项目目录
cd payguard_crew_starter

# 2. 运行部署脚本
.\deploy.ps1

# 3. 选择部署模式（按提示操作）
#    1 = 快速演示（推荐）
#    2 = 开发模式
#    3 = 生产模式
```

### Linux / Mac 用户

```bash
# 1. 进入项目目录
cd payguard_crew_starter

# 2. 运行部署脚本
./deploy.sh

# 3. 选择部署模式（按提示操作）
#    1 = 快速演示（推荐）
#    2 = 开发模式
#    3 = 生产模式
```

---

## 📋 3种部署模式

### 模式1：🚀 快速演示（推荐）

**特点**：
- ✅ 最快启动（< 2分钟）
- ✅ 零配置
- ✅ 使用SQLite
- ✅ 适合演示和测试

**访问地址**：
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

---

### 模式2：💻 开发模式

**特点**：
- ✅ 代码热重载
- ✅ 前后端分离
- ✅ 实时调试
- ✅ 适合本地开发

**访问地址**：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000

---

### 模式3：🏭 生产模式

**特点**：
- ✅ PostgreSQL + Redis
- ✅ 完整前后端栈
- ✅ 生产级配置
- ✅ 适合正式部署

**访问地址**：
- 前端: http://localhost
- 后端API: http://localhost:8000

**注意**：首次运行会自动创建`.env`文件并生成随机密钥

---

## 🔑 默认登录凭据

| 用户 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 分析师 | `demo` | `demo123` |

---

## 📚 常用命令

### 查看日志
```bash
# 实时查看所有日志
docker-compose logs -f

# 只看后端日志
docker-compose logs -f backend

# 只看前端日志  
docker-compose logs -f frontend
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 查看状态
```bash
docker-compose ps
```

---

## 🐛 常见问题

### Q1: 端口被占用

**错误**：`Bind for 0.0.0.0:8000 failed: port is already allocated`

**解决**：
```bash
# Windows
netstat -ano | findstr 8000
taskkill /PID <PID号> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Q2: Docker未安装

**解决**：
- Windows: 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Mac: 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)  
- Linux: `curl -fsSL https://get.docker.com | sh`

### Q3: 服务启动失败

**检查**：
```bash
# 查看详细日志
docker-compose logs

# 重新构建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ 部署成功验证

### 1. 检查服务状态
```bash
docker-compose ps
```

应该看到所有服务状态为 `Up (healthy)`

### 2. 测试后端API
```bash
curl http://localhost:8000/api/health/health
```

应该返回：
```json
{
  "status": "ok",
  "version": "0.2.0",
  ...
}
```

### 3. 访问前端
打开浏览器访问对应地址，应该能看到登录页面

---

## 🎯 下一步

部署成功后：

1. **登录系统**
   - 使用默认凭据登录
   
2. **查看Dashboard**
   - 查看统计数据和图表

3. **测试审计功能**
   - 单笔审计
   - 批量审计

4. **测试审核工作流**
   - 创建审核
   - 审批/拒绝

5. **导出报告**
   - CSV/Excel导出

---

## 📖 更多文档

| 文档 | 说明 |
|------|------|
| [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) | 详细Docker部署指南 |
| [STARTUP_GUIDE.md](STARTUP_GUIDE.md) | 完整启动指南 |
| [LLM_CONFIG_GUIDE.md](LLM_CONFIG_GUIDE.md) | LLM配置指南 |

---

## 🎉 就是这么简单！

```
运行脚本 → 选择模式 → 等待完成 → 开始使用
```

**整个过程只需 2-5 分钟！**
