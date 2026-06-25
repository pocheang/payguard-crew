"""
Agent Prompts Module - Modular Prompt Definitions

提示词模块化架构：
- 每个Agent一个独立文件
- 便于单独修改和更新
- 便于版本控制和协作
- 便于增强和实验

使用方式:
    from app.agents.prompts import TRANSACTION_AGENT_PROMPT
    from app.agents.prompts import FRAUD_DETECTION_AGENT_PROMPT
"""

# 核心Agent提示词
from app.agents.prompts.transaction_agent import TRANSACTION_AGENT_PROMPT
from app.agents.prompts.risk_rule_agent import RISK_RULE_AGENT_PROMPT
from app.agents.prompts.compliance_agent import COMPLIANCE_AGENT_PROMPT
from app.agents.prompts.rag_evidence_agent import RAG_EVIDENCE_AGENT_PROMPT
from app.agents.prompts.report_agent import REPORT_AGENT_PROMPT

# 风险检测Agent提示词
from app.agents.prompts.fraud_detection_agent import FRAUD_DETECTION_AGENT_PROMPT
from app.agents.prompts.merchant_risk_agent import MERCHANT_RISK_AGENT_PROMPT
from app.agents.prompts.device_fingerprint_agent import DEVICE_FINGERPRINT_AGENT_PROMPT
from app.agents.prompts.velocity_check_agent import VELOCITY_CHECK_AGENT_PROMPT

__all__ = [
    # 核心Agent
    "TRANSACTION_AGENT_PROMPT",
    "RISK_RULE_AGENT_PROMPT",
    "COMPLIANCE_AGENT_PROMPT",
    "RAG_EVIDENCE_AGENT_PROMPT",
    "REPORT_AGENT_PROMPT",
    # 风险检测Agent
    "FRAUD_DETECTION_AGENT_PROMPT",
    "MERCHANT_RISK_AGENT_PROMPT",
    "DEVICE_FINGERPRINT_AGENT_PROMPT",
    "VELOCITY_CHECK_AGENT_PROMPT",
]

# Agent分类
CORE_AGENTS = [
    "TRANSACTION_AGENT_PROMPT",
    "RISK_RULE_AGENT_PROMPT",
    "COMPLIANCE_AGENT_PROMPT",
    "RAG_EVIDENCE_AGENT_PROMPT",
    "REPORT_AGENT_PROMPT",
]

RISK_DETECTION_AGENTS = [
    "FRAUD_DETECTION_AGENT_PROMPT",
    "MERCHANT_RISK_AGENT_PROMPT",
    "DEVICE_FINGERPRINT_AGENT_PROMPT",
    "VELOCITY_CHECK_AGENT_PROMPT",
]
