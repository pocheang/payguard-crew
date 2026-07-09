# PayGuard Crew - Agent 完整规格说明

## 📋 总览

PayGuard Crew 包含 **9个专业Agent**，每个都有：
- ✅ 独立的提示词（Prompt）
- ✅ 明确的角色定义（Role）
- ✅ 清晰的目标（Goal）
- ✅ 结构化的输出格式（Expected Output）
- ✅ 本地Fallback逻辑

---

## 🤖 Agent 详细规格

### 1. Transaction Agent（交易分析Agent）

**角色**: Transaction Analyst  
**目标**: 分析交易行为异常，不产生最终评分

**提示词**:
```
分析一笔交易的行为异常和风险点
不分配最终评分、风险等级或决策
识别：交易行为模式、异常特征
```

**输出格式**:
```json
{
  "risk_points": ["风险点1", "风险点2"],
  "behavior_summary": "行为总结"
}
```

**功能**: 
- 分析交易特征
- 识别行为异常
- 提取风险点

---

### 2. Risk Rule Agent（规则解释Agent）

**角色**: Risk Rule Analyst  
**目标**: 解释确定性规则命中，不改变硬决策

**提示词**:
```
解释哪些确定性规则被触发以及为什么重要
不能修改风险评分、风险等级、决策或触发的规则
```

**输出格式**:
```json
{
  "rule_explanation": "规则解释文本"
}
```

**功能**:
- 解释规则触发原因
- 说明规则的重要性
- 不修改规则引擎结果

---

### 3. Compliance Agent（合规审查Agent）

**角色**: Compliance Reviewer  
**目标**: 描述AML或KYC关注点和人工审核理由

**提示词**:
```
审查KYC状态、账户年龄、交易频率
解释AML和KYC关注点
判断是否需要人工审核
不能覆盖确定性规则的硬决策
```

**输出格式**:
```json
{
  "compliance_notes": ["合规注释1", "合规注释2"],
  "manual_review_reason": "人工审核原因"
}
```

**功能**:
- KYC/AML合规检查
- 识别人工审核需求
- 提供合规建议

---

### 4. RAG Evidence Agent（证据检索Agent）

**角色**: Evidence Retriever  
**目标**: 总结提供的证据，不发明来源

**提示词**:
```
基于检索到的证据列表总结相关性
只使用提供的证据列表
不能发明、重命名或添加证据来源
```

**输出格式**:
```json
{
  "evidence_summary": "证据摘要"
}
```

**功能**:
- 检索相关政策文档
- 总结证据相关性
- 提供审计依据

---

### 5. Report Agent（报告生成Agent）

**角色**: Audit Reporter  
**目标**: 生成最终审计报告，保留确定性输出

**提示词**:
```
基于规则结果、合规注释、交易发现和证据生成最终报告
必须精确保留确定性的风险评分、风险等级、决策和证据来源
```

**输出格式**:
```json
{
  "summary": "审计摘要",
  "suggestion": "操作建议"
}
```

**功能**:
- 整合所有信息
- 生成审计报告
- 提供操作建议

---

### 6. Fraud Detection Agent（欺诈检测Agent）⭐

**角色**: Fraud Detection Specialist  
**目标**: 识别欺诈模式和行为异常

**提示词**:
```
分析行为异常，识别欺诈模式：
- 账户接管（Account Takeover）
- 信用卡测试（Card Testing）
- 速度滥用（Velocity Abuse）
- 地理位置不一致
- 时间模式异常
- 商户类别不匹配
不做最终决策，只提供欺诈指标
```

**输出格式**:
```json
{
  "fraud_indicators": ["检测到的欺诈模式"],
  "anomaly_score": 85,
  "fraud_type": "account_takeover",
  "confidence": "high"
}
```

**功能**:
- 检测账户接管
- 识别卡测试
- 发现速度滥用
- 评估欺诈置信度

---

### 7. Merchant Risk Agent（商户风险Agent）⭐

**角色**: Merchant Risk Analyst  
**目标**: 评估商户声誉和识别高风险商户类别

**提示词**:
```
评估商户数据、交易历史、商户类别、历史退单率
识别高风险商户类别：
- 加密货币（Crypto）
- 博彩（Gambling）
- 成人内容（Adult Content）
分析：退单率、业务存续时间、行业风险、合规历史
```

**输出格式**:
```json
{
  "merchant_risk_factors": ["风险因素"],
  "merchant_reputation_score": 75,
  "high_risk_category": true,
  "recommendation": "建议"
}
```

**功能**:
- 评估商户声誉
- 识别高风险行业
- 分析退单率
- 提供风险建议

---

### 8. Device Fingerprint Agent（设备指纹Agent）⭐

**角色**: Device Security Analyst  
**目标**: 分析设备指纹，检测设备欺诈信号

**提示词**:
```
分析设备信息：device_id、IP地址、浏览器指纹、操作系统、位置
检测：
- 设备异常
- 模拟器（Emulator）
- VPN/代理（Proxy）使用
- 设备欺骗（Spoofing）
- 单设备多账户速度
分析：设备一致性、位置跳跃、已知恶意设备、设备-账户关联
```

**输出格式**:
```json
{
  "device_risk_signals": ["设备风险信号"],
  "device_trust_score": 65,
  "is_emulator": false,
  "is_vpn_proxy": true,
  "device_reputation": "suspicious"
}
```

**功能**:
- 检测模拟器
- 识别VPN/代理
- 设备指纹分析
- 设备声誉评估

---

### 9. Velocity Check Agent（速度检查Agent）⭐

**角色**: Velocity Monitor  
**目标**: 检测速度滥用模式和交易频率异常

**提示词**:
```
分析交易数据和时间序列历史（1小时、24小时、7天、30天）
检测速度滥用模式：
- 快速连续交易
- 突发活动（Burst Activity）
- 异常时间模式
分析：交易频率、金额速度、商户速度、时间模式
```

**输出格式**:
```json
{
  "velocity_violations": ["速度违规"],
  "velocity_risk_score": 45,
  "burst_detected": true,
  "time_pattern_anomaly": false,
  "recommendation": "建议"
}
```

**功能**:
- 监控交易频率
- 检测突发活动
- 识别时间模式异常
- 评估速度风险

---

## 🔄 Agent 工作流程

```
用户请求
   ↓
阶段1: Transaction Agent → 分析交易特征
   ↓
阶段2: 规则引擎 → 评估风险
   ↓
阶段3: 6个Agent并行 ⚡
   ├─ Risk Rule Agent → 解释规则
   ├─ Compliance Agent → 合规审查
   ├─ Fraud Detection Agent → 欺诈检测 ⭐
   ├─ Merchant Risk Agent → 商户风险 ⭐
   ├─ Device Fingerprint Agent → 设备分析 ⭐
   └─ Velocity Check Agent → 速度检查 ⭐
   ↓
阶段4: RAG Evidence Agent → 检索证据
   ↓
阶段5: Report Agent → 生成报告
   ↓
返回完整审计结果
```

---

## 📊 Agent 对比表

| Agent | 输入 | 输出 | 主要功能 | 是否并行 |
|-------|------|------|----------|---------|
| Transaction | 交易JSON | 风险点+行为摘要 | 交易分析 | ❌ |
| Risk Rule | 交易+规则结果 | 规则解释 | 规则说明 | ✅ |
| Compliance | 交易+KYC+规则 | 合规注释 | 合规审查 | ✅ |
| Fraud Detection | 交易+历史 | 欺诈指标 | 欺诈检测 | ✅ |
| Merchant Risk | 商户+历史 | 商户风险 | 商户评估 | ✅ |
| Device Fingerprint | 设备信息 | 设备风险 | 设备分析 | ✅ |
| Velocity Check | 交易+时序 | 速度风险 | 速度监控 | ✅ |
| RAG Evidence | 查询+证据 | 证据摘要 | 证据检索 | ❌ |
| Report | 所有结果 | 最终报告 | 报告生成 | ❌ |

---

## 🎯 设计原则

### 1. 职责分离
- 每个Agent只负责一个特定领域
- 不重复其他Agent的工作
- 输出格式标准化

### 2. 确定性优先
- 硬规则由规则引擎处理
- Agent只做分析和解释
- 不修改确定性结果

### 3. 可扩展性
- 新增Agent只需：
  1. 在prompts.py添加提示词
  2. 在agent_factory.py注册
  3. 在fallbacks/添加本地逻辑
  4. 在parsers.py添加解析器
  5. 在agents/添加执行函数

### 4. 双模式运行
- **CrewAI模式**: 使用LLM进行智能分析
- **本地模式**: 使用确定性逻辑作为Fallback
- 自动降级，保证可用性

---

## 💡 使用示例

### 查看Agent信息

```python
from app.agents.agent_factory import build_agent_registry

registry = build_agent_registry()

# 列出所有Agent
for name, spec in registry.items():
    print(f"{name}: {spec.role} - {spec.goal}")

# 查看特定Agent
fraud_agent = registry["fraud_detection_agent"]
print(f"提示词: {fraud_agent.prompt}")
print(f"输出格式: {fraud_agent.expected_output}")
print(f"运行模式: {fraud_agent.backend}")
```

### 单独测试Agent

```python
from app.crew.agents import run_fraud_detection_agent

# 准备交易数据
tx = TransactionInput(...)
tx_payload = tx.model_dump()

# 执行欺诈检测
fraud_output, log = await run_fraud_detection_agent(
    tx, tx_payload, registry, False
)

print(f"欺诈指标: {fraud_output['fraud_indicators']}")
print(f"异常评分: {fraud_output['anomaly_score']}")
```

---

## 🏆 总结

✅ **9个专业Agent** - 完整的风控体系  
✅ **标准化接口** - 统一的输入输出格式  
✅ **清晰的职责** - 每个Agent专注一个领域  
✅ **双模式运行** - CrewAI + 本地Fallback  
✅ **高度可扩展** - 易于添加新Agent  
✅ **生产就绪** - 完整的错误处理和日志  

每个Agent都有完整的：
- ✅ 提示词定义
- ✅ 功能说明
- ✅ 输出格式
- ✅ Fallback逻辑
- ✅ 解析器
- ✅ 执行函数

**PayGuard Crew的Agent系统是完整、规范、可扩展的企业级实现！**

---

生成时间: 2026-06-25
版本: v0.1.6
状态: ✅ 完整规格
