"""
Agent runners package - Modular agent execution
"""
from app.crew.agents.core_agents import (
    run_transaction_agent,
    run_risk_rule_agent,
    run_compliance_agent,
)
from app.crew.agents.risk_agents import (
    run_fraud_detection_agent,
    run_merchant_risk_agent,
    run_device_fingerprint_agent,
    run_velocity_check_agent,
)
from app.crew.agents.evidence_agents import (
    run_rag_agent,
    run_report_agent,
)

__all__ = [
    # Core agents
    "run_transaction_agent",
    "run_risk_rule_agent",
    "run_compliance_agent",
    # Risk detection agents
    "run_fraud_detection_agent",
    "run_merchant_risk_agent",
    "run_device_fingerprint_agent",
    "run_velocity_check_agent",
    # Evidence and report agents
    "run_rag_agent",
    "run_report_agent",
]
