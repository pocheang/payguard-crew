# PayGuard LLM模型配置指南

## 🤖 模型概览

PayGuard 支持 **3种运行模式**：

1. **规则引擎模式**（默认）- 不需要LLM，纯规则驱动 ✅ 推荐用于demo
2. **LLM增强模式** - 使用AI模型提升分析能力
3. **CrewAI编排模式** - 多Agent协作，最强大但需要配置

---

## 🚀 快速开始（无需LLM）

### 规则引擎模式 - 零配置启动 ⭐

**优点**：
- ✅ 无需API密钥
- ✅ 无成本
- ✅ 快速响应
- ✅ 完全离线工作
- ✅ 适合演示和测试

**配置**（`.env`文件）：
```bash
# LLM配置 - 禁用模式（默认）
LLM_PROVIDER=disabled

# CrewAI配置 - 关闭
ENABLE_CREWAI=false
```

**功能**：
- ✅ 单笔交易审计
- ✅ 批量审计
- ✅ 风险评分
- ✅ 规则匹配
- ✅ 审核工作流
- ✅ 报告导出

> **推荐**：Demo演示直接使用此模式，功能完整且稳定！

---

## 🎯 支持的LLM提供商

### 1. OpenAI（GPT系列）

**推荐模型**：
- `gpt-4o-mini` - 最快，成本低 ⭐ 推荐
- `gpt-4o` - 最强，成本高
- `gpt-3.5-turbo` - 经济型

**配置**（`.env`）：
```bash
# 选择OpenAI
LLM_PROVIDER=openai

# OpenAI配置
OPENAI_API_KEY=sk-your-actual-openai-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=  # 留空使用默认，或自定义地址

# 启用CrewAI（可选）
ENABLE_CREWAI=false  # true启用多Agent编排
```

**获取API密钥**：
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 创建API密钥
4. 充值账户余额

**成本估算**（gpt-4o-mini）：
- 输入：$0.15 / 1M tokens
- 输出：$0.60 / 1M tokens
- 单次审计约：$0.001 - $0.005

---

### 2. DeepSeek（推荐国内用户）🇨🇳

**推荐模型**：
- `deepseek-chat` - 性价比最高 ⭐⭐⭐

**优点**：
- 🚀 速度快
- 💰 成本低（比OpenAI便宜10倍）
- 🇨🇳 国内访问稳定
- 🎯 中文理解优秀

**配置**（`.env`）：
```bash
# 选择DeepSeek
LLM_PROVIDER=deepseek

# DeepSeek配置
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 启用CrewAI（可选）
ENABLE_CREWAI=false
```

**获取API密钥**：
1. 访问 https://platform.deepseek.com/
2. 注册账号（支持国内手机号）
3. 创建API密钥
4. 充值（支持支付宝/微信）

**成本估算**：
- 输入：¥0.001 / 1K tokens
- 输出：¥0.002 / 1K tokens
- 单次审计约：¥0.01 - ¥0.05（约$0.0014）

> **推荐**：如果要启用LLM，国内用户首选DeepSeek！

---

### 3. Ollama（本地部署）🏠

**推荐模型**：
- `qwen2.5` - 通义千问2.5 ⭐
- `llama3.1` - Meta Llama
- `mistral` - Mistral AI

**优点**：
- ✅ 完全免费
- ✅ 数据隐私（本地运行）
- ✅ 无网络依赖
- ✅ 无成本

**缺点**：
- ❌ 需要本地GPU（推荐16GB+）
- ❌ 安装配置复杂
- ❌ 性能略低于云端模型

**配置**（`.env`）：
```bash
# 选择Ollama
LLM_PROVIDER=ollama

# Ollama配置
OLLAMA_MODEL=qwen2.5
OLLAMA_BASE_URL=http://localhost:11434/v1

# 启用CrewAI（可选）
ENABLE_CREWAI=false
```

**安装Ollama**：
```bash
# 1. 安装Ollama
# Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装包: https://ollama.com/download

# 2. 下载模型
ollama pull qwen2.5

# 3. 启动服务
ollama serve

# 4. 测试
curl http://localhost:11434/api/version
```

---

## 🎭 CrewAI多Agent编排

### 什么是CrewAI？

CrewAI将多个AI Agent组织成团队协作完成复杂任务。

**PayGuard的Agent团队**：
1. **Transaction Agent** - 交易数据分析
2. **Risk Rule Agent** - 规则匹配
3. **Compliance Agent** - 合规检查
4. **Fraud Detection Agent** - 欺诈检测
5. **Merchant Risk Agent** - 商户风险评估
6. **Device Fingerprint Agent** - 设备指纹分析
7. **Velocity Check Agent** - 频率检查
8. **RAG Agent** - 知识库查询
9. **Report Agent** - 报告生成

### 启用CrewAI

**配置**（`.env`）：
```bash
# 必须先配置LLM提供商
LLM_PROVIDER=openai  # 或 deepseek/ollama

# 对应的API密钥
OPENAI_API_KEY=sk-xxx

# 启用CrewAI
ENABLE_CREWAI=true

# RAG配置（可选）
RAG_TOP_K=3
PAYGUARD_DOCS_DIR=docs
```

**优点**：
- 🧠 更智能的分析
- 📊 更详细的报告
- 🔍 上下文理解能力

**缺点**：
- 💰 成本更高（多次API调用）
- ⏱️ 响应时间更长
- 🔧 配置复杂

---

## ⚙️ 高级配置

### 超时和重试

```bash
# LLM超时时间（秒）
LLM_TIMEOUT_SECONDS=30

# 最大重试次数
LLM_MAX_RETRIES=2
```

### RAG知识库

```bash
# 检索返回数量
RAG_TOP_K=3

# 知识库目录
PAYGUARD_DOCS_DIR=docs
```

---

## 🔍 配置验证

### 检查当前配置

```bash
# 启动后端
uvicorn app.main:app --reload

# 访问健康检查
curl http://localhost:8000/api/health/health

# 查看LLM配置
curl http://localhost:8000/ | jq
```

**返回示例**（规则引擎模式）：
```json
{
  "service": "payguard-crew",
  "version": "0.2.0",
  "environment": "dev",
  "features": {
    "jwt_auth": true,
    "rbac": true,
    "llm_enabled": false,  // ← LLM状态
    "crewai_enabled": false  // ← CrewAI状态
  }
}
```

---

## 📊 模式对比

| 特性 | 规则引擎 | OpenAI | DeepSeek | Ollama | CrewAI |
|------|---------|--------|----------|--------|--------|
| **成本** | 免费 ✅ | 中等 | 低 | 免费 ✅ | 高 |
| **速度** | 快 ✅ | 快 | 快 | 中等 | 慢 |
| **准确性** | 高 ✅ | 最高 | 高 | 中等 | 最高 |
| **配置难度** | 零配置 ✅ | 简单 | 简单 | 复杂 | 复杂 |
| **网络依赖** | 无 ✅ | 需要 | 需要 | 无 ✅ | 需要 |
| **数据隐私** | 完全本地 ✅ | 云端 | 云端 | 完全本地 ✅ | 云端 |
| **国内访问** | ✅ | ❌ | ✅ | ✅ | 视提供商 |

---

## 🎯 推荐配置方案

### 方案1：快速Demo（推荐）⭐⭐⭐

```bash
LLM_PROVIDER=disabled
ENABLE_CREWAI=false
```

**适合**：演示、测试、开发
**优点**：零配置、快速、免费

---

### 方案2：国内生产环境（推荐）⭐⭐

```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
ENABLE_CREWAI=false
```

**适合**：国内部署、成本敏感
**优点**：访问稳定、成本低、性能好

---

### 方案3：国际生产环境

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
ENABLE_CREWAI=false
```

**适合**：国际部署、追求性能
**优点**：响应快、质量高、生态成熟

---

### 方案4：完全离线部署

```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5
OLLAMA_BASE_URL=http://localhost:11434/v1
ENABLE_CREWAI=false
```

**适合**：数据敏感、无外网
**优点**：完全本地、数据安全

---

### 方案5：高级AI增强（慎用）

```bash
LLM_PROVIDER=openai  # 或 deepseek
OPENAI_API_KEY=sk-xxx
ENABLE_CREWAI=true
RAG_TOP_K=3
```

**适合**：复杂场景、需要深度分析
**缺点**：成本高、速度慢

---

## 🔧 配置步骤

### 步骤1：选择模式

根据上面的对比表选择合适的模式。

### 步骤2：编辑 .env 文件

```bash
cp .env.example .env
nano .env  # 或使用你喜欢的编辑器
```

### 步骤3：填写配置

根据选择的模式填写对应的配置项。

### 步骤4：启动系统

```bash
# 后端
uvicorn app.main:app --reload

# 前端
cd frontend && npm run dev
```

### 步骤5：验证配置

访问 http://localhost:8000/api/health/health 查看配置状态。

---

## ⚠️ 常见问题

### Q1: 不配置LLM能正常使用吗？

**A**: ✅ 完全可以！规则引擎模式功能完整，推荐用于demo。

### Q2: 哪个LLM提供商最便宜？

**A**: DeepSeek（国内）或 gpt-4o-mini（国际）

### Q3: CrewAI必须启用吗？

**A**: ❌ 不需要。关闭CrewAI仍有完整功能，且速度更快。

### Q4: Ollama需要什么配置？

**A**: 推荐16GB+ GPU内存，RTX 3060或更高。

### Q5: 如何切换LLM提供商？

**A**: 修改 `.env` 中的 `LLM_PROVIDER` 和对应的API密钥，重启服务。

### Q6: API密钥如何保密？

**A**: 
- ✅ `.env` 文件不要提交到Git（已在.gitignore）
- ✅ 使用环境变量注入（Docker/K8s）
- ✅ 定期轮换密钥

---

## 📚 相关文档

- **OpenAI文档**: https://platform.openai.com/docs
- **DeepSeek文档**: https://platform.deepseek.com/docs
- **Ollama文档**: https://ollama.com/docs
- **CrewAI文档**: https://docs.crewai.com/

---

## 🆘 获取帮助

如果配置遇到问题：

1. 查看后端日志：终端输出
2. 检查健康状态：`curl http://localhost:8000/api/health/health`
3. 验证API密钥：确保不是示例密钥
4. 查看错误日志：`logs/` 目录

---

**推荐配置（快速开始）**：
```bash
# 零配置，立即可用
LLM_PROVIDER=disabled
ENABLE_CREWAI=false
```

**🎉 这样就可以开始使用PayGuard了！**
