# 依赖安装指南

**更新日期**: 2026-06-28

---

## 📦 安装依赖

### 方法1: 完整安装（推荐）

```bash
# 安装所有依赖
pip install -r requirements.txt
```

### 方法2: 核心依赖（最小化）

如果只想运行核心功能，不需要AI功能：

```bash
# 核心依赖
pip install fastapi==0.115.0
pip install uvicorn[standard]==0.30.6
pip install pydantic==2.9.2
pip install python-dotenv==1.0.1
pip install slowapi==0.1.9
pip install PyJWT==2.9.0
pip install cryptography==43.0.1
pip install sqlalchemy==2.0.35
```

### 方法3: 分类安装

```bash
# 1. 核心框架
pip install fastapi uvicorn pydantic python-dotenv slowapi

# 2. 安全认证
pip install PyJWT cryptography passlib[bcrypt]

# 3. 数据库
pip install sqlalchemy

# 4. 可选：AI功能
pip install crewai langchain langchain-openai chromadb openai

# 5. 可选：监控
pip install prometheus-client sentry-sdk opentelemetry-api

# 6. 可选：Redis（生产环境）
pip install redis hiredis
```

---

## 🔍 验证安装

```bash
# 测试导入
python -c "from app.main import app; print('✓ 所有依赖已安装')"
```

如果出现 `ModuleNotFoundError`，安装对应的包：

| 错误 | 解决方案 |
|------|----------|
| `No module named 'slowapi'` | `pip install slowapi` |
| `No module named 'fastapi'` | `pip install fastapi` |
| `No module named 'pydantic'` | `pip install pydantic` |
| `No module named 'crewai'` | `pip install crewai` （可选）|

---

## 🚀 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成密钥
python scripts/generate_secrets.py

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，粘贴密钥

# 4. 启动应用
python -m app.main
```

---

## ⚠️ 常见问题

### Q: pip install 很慢怎么办？

使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 某个依赖安装失败？

跳过该依赖继续安装：
```bash
pip install -r requirements.txt --ignore-requires-python
```

### Q: 不需要AI功能可以不装吗？

可以！注释掉requirements.txt中的AI部分：
```
# AI Features (Optional) - 可以注释掉
# crewai==0.86.0
# langchain==0.3.1
# ...
```

---

**最小依赖**: 只需要前17行（核心+安全+数据库）
