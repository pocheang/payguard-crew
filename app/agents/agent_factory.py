from dataclasses import dataclass
from typing import Any

from app.agents.prompts import (
    COMPLIANCE_AGENT_PROMPT,
    RAG_EVIDENCE_AGENT_PROMPT,
    REPORT_AGENT_PROMPT,
    RISK_RULE_AGENT_PROMPT,
    TRANSACTION_AGENT_PROMPT,
    FRAUD_DETECTION_AGENT_PROMPT,
    MERCHANT_RISK_AGENT_PROMPT,
    DEVICE_FINGERPRINT_AGENT_PROMPT,
    VELOCITY_CHECK_AGENT_PROMPT,
)
from app.config import Settings, get_settings


@dataclass
class AgentSpec:
    name: str
    role: str
    goal: str
    prompt: str
    expected_output: str
    task_key: str
    backend: str
    instance: Any | None = None



def _build_crewai_llm(settings: Settings) -> Any | None:
    if not (settings.enable_crewai and settings.llm_enabled):
        return None

    try:
        from crewai import LLM
    except ImportError:
        return None

    last_error: Exception | None = None
    for model_name in settings.crewai_model_candidates:
        try:
            kwargs = {
                "model": model_name,
                "timeout": settings.llm_timeout_seconds,
                "max_retries": settings.llm_max_retries,
            }
            if settings.active_api_key:
                kwargs["api_key"] = settings.active_api_key
            if settings.active_base_url:
                kwargs["base_url"] = settings.active_base_url
            return LLM(**kwargs)
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        return None
    return None



def build_agent_registry() -> dict[str, AgentSpec]:
    settings = get_settings()
    crewai_enabled = settings.enable_crewai and settings.llm_enabled
    crewai_llm = _build_crewai_llm(settings)

    try:
        from crewai import Agent
    except ImportError:
        crewai_enabled = False
        Agent = None  # type: ignore[assignment]

    agent_definitions = [
        (
            "transaction_agent",
            "Transaction Analyst",
            "Analyze transaction behavior anomalies without producing a final score.",
            TRANSACTION_AGENT_PROMPT,
            'Strict JSON with keys "risk_points" and "behavior_summary".',
            "transaction_findings",
        ),
        (
            "risk_rule_agent",
            "Risk Rule Analyst",
            "Explain deterministic rule hits without changing the hard decision.",
            RISK_RULE_AGENT_PROMPT,
            'Strict JSON with key "rule_explanation".',
            "rule_explanation",
        ),
        (
            "compliance_agent",
            "Compliance Reviewer",
            "Describe AML or KYC concerns and manual-review rationale.",
            COMPLIANCE_AGENT_PROMPT,
            'Strict JSON with keys "compliance_notes" and "manual_review_reason".',
            "compliance_result",
        ),
        (
            "rag_evidence_agent",
            "Evidence Retriever",
            "Summarize only the provided evidence without inventing sources.",
            RAG_EVIDENCE_AGENT_PROMPT,
            'Strict JSON with key "evidence_summary".',
            "evidence_result",
        ),
        (
            "report_agent",
            "Audit Reporter",
            "Generate the final audit wording while preserving deterministic outputs.",
            REPORT_AGENT_PROMPT,
            'Strict JSON with keys "summary" and "suggestion".',
            "final_report",
        ),
        (
            "fraud_detection_agent",
            "Fraud Detection Specialist",
            "Identify fraud patterns and behavioral anomalies in transactions.",
            FRAUD_DETECTION_AGENT_PROMPT,
            'Strict JSON with keys "fraud_indicators", "anomaly_score", "fraud_type", "confidence".',
            "fraud_detection_result",
        ),
        (
            "merchant_risk_agent",
            "Merchant Risk Analyst",
            "Assess merchant reputation and identify high-risk merchant categories.",
            MERCHANT_RISK_AGENT_PROMPT,
            'Strict JSON with keys "merchant_risk_factors", "merchant_reputation_score", "high_risk_category", "recommendation".',
            "merchant_risk_result",
        ),
        (
            "device_fingerprint_agent",
            "Device Security Analyst",
            "Analyze device fingerprints and detect device-based fraud signals.",
            DEVICE_FINGERPRINT_AGENT_PROMPT,
            'Strict JSON with keys "device_risk_signals", "device_trust_score", "is_emulator", "is_vpn_proxy", "device_reputation".',
            "device_fingerprint_result",
        ),
        (
            "velocity_check_agent",
            "Velocity Monitor",
            "Detect velocity abuse patterns and transaction frequency anomalies.",
            VELOCITY_CHECK_AGENT_PROMPT,
            'Strict JSON with keys "velocity_violations", "velocity_risk_score", "burst_detected", "time_pattern_anomaly", "recommendation".',
            "velocity_check_result",
        ),
    ]

    registry: dict[str, AgentSpec] = {}
    for name, role, goal, prompt, expected_output, task_key in agent_definitions:
        instance = None
        if crewai_enabled and Agent is not None and crewai_llm is not None:
            try:
                instance = Agent(
                    role=role,
                    goal=goal,
                    backstory=prompt.strip(),
                    allow_delegation=False,
                    verbose=False,
                    llm=crewai_llm,
                )
            except Exception:
                instance = None
        registry[name] = AgentSpec(
            name=name,
            role=role,
            goal=goal,
            prompt=prompt.strip(),
            expected_output=expected_output,
            task_key=task_key,
            backend="crewai" if instance is not None else "local",
            instance=instance,
        )

    return registry
