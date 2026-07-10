# 演示指南

> **版本**: v0.2.0  
> **更新**: 2026-07-10

---

## 📋 目录

- [快速演示](#快速演示)
- [演示场景](#演示场景)
- [功能展示](#功能展示)
- [常见问题](#常见问题)

---

## 快速演示

### 启动演示环境

**方式1: 一键启动**
```bash
# Windows
.\start.bat

# Linux/Mac
./start.sh
```

**方式2: Docker启动**
```bash
docker-compose up -d
```

### 访问系统

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 默认账号

```
管理员: admin / admin123
演示账号: demo / demo123
```

---

## 演示场景

### 场景1: 单笔交易风控审计

**目标**: 展示实时风险评估能力

1. **进入审计页面**
   - 访问 http://localhost:3000/audit

2. **填写交易信息**
   ```json
   {
     "transaction_id": "TX001",
     "user_id": "user_123",
     "merchant_id": "merchant_456",
     "amount": 15000,
     "currency": "CNY"
   }
   ```

3. **查看审计结果**
   - 风险评分
   - 触发的规则
   - AI分析建议
   - 决策建议（通过/拒绝/人工审核）

**演示要点**:
- ✅ 毫秒级响应
- ✅ 多维度风险评估
- ✅ AI增强分析
- ✅ 可解释的决策

### 场景2: 批量交易审计

**目标**: 展示高吞吐量处理能力

1. **进入批量审计页面**
   - 访问 http://localhost:3000/batch

2. **上传批量数据**（CSV/JSON）
   ```csv
   transaction_id,user_id,amount,currency
   TX001,user_123,10000,CNY
   TX002,user_456,50000,CNY
   TX003,user_789,5000,CNY
   ```

3. **查看批处理结果**
   - 总数/成功/失败统计
   - 风险分布图表
   - 导出详细报告

**演示要点**:
- ✅ 支持100笔并发
- ✅ 实时进度展示
- ✅ 批量结果统计
- ✅ 报告导出功能

### 场景3: 人工审核工作流

**目标**: 展示完整的审核闭环

1. **查看待审核列表**
   - 访问 http://localhost:3000/review

2. **审核高风险交易**
   - 查看风险详情
   - AI分析建议
   - 历史行为分析

3. **做出审核决策**
   - 批准/拒绝/要求补充资料
   - 填写审核意见
   - 查看审核历史

**演示要点**:
- ✅ 优先级队列
- ✅ 多维度信息展示
- ✅ 审核流转跟踪
- ✅ 审核员绩效统计

### 场景4: 实时监控Dashboard

**目标**: 展示数据可视化和监控能力

1. **访问Dashboard**
   - http://localhost:3000/dashboard

2. **查看实时指标**
   - 今日交易总额
   - 风险交易占比
   - 审核通过率
   - 系统响应时间

3. **查看图表分析**
   - 风险趋势图
   - 交易分布饼图
   - 审核工作量柱状图
   - 时间序列分析

**演示要点**:
- ✅ 实时数据更新
- ✅ 多维度可视化
- ✅ 交互式图表
- ✅ 数据钻取分析

### 场景5: 规则管理

**目标**: 展示灵活的规则配置能力

1. **访问规则管理**
   - http://localhost:3000/rules

2. **创建自定义规则**
   ```json
   {
     "name": "大额交易规则",
     "type": "amount",
     "condition": "amount > 10000",
     "weight": 8,
     "action": "review"
   }
   ```

3. **测试规则效果**
   - 输入测试数据
   - 查看规则匹配结果
   - 调整规则参数

4. **查看规则统计**
   - 触发次数
   - 准确率
   - 误报率

**演示要点**:
- ✅ 可视化规则配置
- ✅ 实时规则测试
- ✅ 规则版本管理
- ✅ 规则效果分析

---

## 功能展示

### 核心功能清单

#### 1. 风险审计
- [x] 单笔交易审计
- [x] 批量交易审计（最多100笔）
- [x] 实时风险评分
- [x] 多规则引擎
- [x] AI增强分析
- [x] 审计报告导出

#### 2. 审核工作流
- [x] 待审核队列
- [x] 优先级管理
- [x] 审核员分配
- [x] 审核历史追踪
- [x] 超时提醒
- [x] 审核统计

#### 3. 规则管理
- [x] 规则CRUD操作
- [x] 规则测试验证
- [x] 规则版本控制
- [x] 规则效果统计
- [x] 规则激活/停用

#### 4. 数据可视化
- [x] 实时Dashboard
- [x] 风险趋势图
- [x] 交易分布图
- [x] 审核工作量图
- [x] 时间序列分析

#### 5. 系统管理
- [x] API密钥管理
- [x] 用户权限管理
- [x] 审计日志查询
- [x] 系统配置
- [x] 性能监控

### 技术亮点

#### 性能指标
- ⚡ 响应时间: < 100ms（规则引擎）
- ⚡ 吞吐量: 1000+ TPS
- ⚡ 并发支持: 100笔批量审计
- ⚡ 前端加载: < 2s

#### 技术特性
- 🔒 多层安全防护
- 🚀 前端性能优化（-98.6%体积）
- 🐳 Docker一键部署
- 📊 ECharts可视化
- 🤖 多LLM支持（OpenAI/DeepSeek/Ollama）
- 🧪 60%+测试覆盖率

---

## 演示技巧

### 1. 准备工作

**检查清单**:
- [ ] 服务已启动（docker-compose ps）
- [ ] 数据库已初始化
- [ ] 演示数据已加载
- [ ] 浏览器已打开
- [ ] 账号已准备

**测试连接**:
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问
curl http://localhost:3000
```

### 2. 演示顺序建议

**标准流程（15分钟）**:
1. Dashboard概览（2分钟）
2. 单笔审计（3分钟）
3. 批量审计（3分钟）
4. 人工审核（4分钟）
5. 规则管理（3分钟）

**快速演示（5分钟）**:
1. Dashboard（1分钟）
2. 单笔审计（2分钟）
3. 人工审核（2分钟）

**完整演示（30分钟）**:
- 以上所有场景 + 问答

### 3. 演示话术

**开场**:
> "PayGuard是一个基于AI的企业级支付风控系统，提供毫秒级的实时风险评估和完整的审核工作流。让我们通过几个实际场景来展示系统的核心能力。"

**单笔审计**:
> "这是一笔1.5万元的交易，系统在100毫秒内完成了风险评估，触发了大额交易规则，风险评分75分，建议人工审核。AI分析给出了详细的风险解读和处理建议。"

**批量审计**:
> "对于批量场景，系统支持一次提交100笔交易，并发处理，实时显示进度。处理完成后可以看到风险分布统计和详细报告。"

**人工审核**:
> "高风险交易会进入审核队列。审核员可以看到完整的交易信息、风险分析、历史行为，做出批准或拒绝的决策，整个流程可追溯。"

### 4. 常见提问准备

**Q: 系统支持哪些LLM？**
> A: 支持OpenAI GPT系列、DeepSeek（国内推荐）、Ollama本地部署。可以根据需求灵活切换。

**Q: 性能如何？**
> A: 单机1000+ TPS，响应时间<100ms，前端加载<2s。经过专业性能优化。

**Q: 如何部署？**
> A: 提供Docker一键部署，支持开发和生产两种模式。生产环境使用PostgreSQL+Redis+Nginx。

**Q: 规则如何配置？**
> A: 提供可视化的规则管理界面，支持实时测试和版本控制。规则可以基于金额、频率、地域等多个维度。

**Q: 是否支持定制？**
> A: 代码完全开源，架构清晰，文档完善，方便二次开发和功能扩展。

---

## 常见问题

### 启动失败

**问题**: 端口已占用
```bash
# 检查端口
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 修改端口（docker-compose.yml）
ports:
  - "8001:8000"  # 后端改为8001
  - "3001:3000"  # 前端改为3001
```

**问题**: 数据库连接失败
```bash
# 检查数据库
docker-compose logs backend | grep -i database

# 重新初始化
docker-compose down -v
docker-compose up -d
```

### 数据问题

**问题**: 没有演示数据
```bash
# 手动加载演示数据
docker-compose exec backend python -m app.scripts.load_demo_data

# 或通过API
curl -X POST http://localhost:8000/api/admin/load-demo-data \
  -H "X-API-Key: dev-key-123"
```

**问题**: 数据清空
```bash
# 重置数据库
docker-compose down -v
docker-compose up -d
```

### UI问题

**问题**: 前端白屏
```bash
# 检查前端日志
docker-compose logs frontend

# 重新构建
docker-compose up -d --build frontend
```

**问题**: API调用失败
```javascript
// 检查API配置（frontend/src/services/api.js）
const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'
```

### LLM问题

**问题**: LLM无响应
```bash
# 检查Ollama连接（Windows/Mac）
curl http://host.docker.internal:11434/api/tags

# 检查OpenAI配置
echo $OPENAI_API_KEY
```

---

## 演示资源

### 测试数据

**正常交易**:
```json
{
  "transaction_id": "TX_NORMAL_001",
  "user_id": "user_123",
  "amount": 500,
  "currency": "CNY"
}
```

**可疑交易**:
```json
{
  "transaction_id": "TX_SUSPECT_001",
  "user_id": "user_456",
  "amount": 50000,
  "currency": "CNY",
  "location": {"country": "NG"}
}
```

**高风险交易**:
```json
{
  "transaction_id": "TX_HIGH_RISK_001",
  "user_id": "user_789",
  "amount": 100000,
  "currency": "CNY",
  "frequency": "10_transactions_in_hour"
}
```

### 批量测试文件

见 `tests/data/demo_transactions.csv`

---

## 相关文档

- [快速开始](QUICK_START.md)
- [API文档](../api/API_DOCUMENTATION.md)
- [Docker部署](DOCKER.md)
- [故障排除](TROUBLESHOOTING.md)

---

**维护者**: PayGuard Team  
**更新**: 2026-07-10
