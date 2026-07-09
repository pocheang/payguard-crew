"""
审计结果解析器（增强版，带Schema验证）
"""
from typing import Any
import logging

from app.crew.schemas import AGENT_SCHEMAS
from app.crew.schemas.validator import validate_agent_output

logger = logging.getLogger(__name__)

JSONDict = dict[str, Any]


def parse_transaction_findings(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析交易发现结果（带Schema验证）"""
    if not payload:
        return None

    # 🔧 Schema验证
    is_valid, error_msg = validate_agent_output("transaction_agent", payload, AGENT_SCHEMAS.get("transaction_agent"))
    if not is_valid:
        logger.warning(f"Transaction agent output validation failed: {error_msg}")
        return None

    risk_points = payload.get("risk_points")
    behavior_summary = payload.get("behavior_summary")
    if not isinstance(risk_points, list) or not all(
        isinstance(item, str) for item in risk_points
    ):
        return None
    if not isinstance(behavior_summary, str) or not behavior_summary.strip():
        return None
    return {
        "risk_points": [item.strip() for item in risk_points if item.strip()],
        "behavior_summary": behavior_summary.strip(),
    }


def parse_rule_explanation(payload: JSONDict | None) -> str | None:
    """解析规则解释（带Schema验证）"""
    if not payload:
        return None

    # 🔧 新增：Schema验证
    is_valid, error_msg = validate_agent_output("risk_rule_agent", payload)
    if not is_valid:
        logger.warning(f"Risk rule agent output validation failed: {error_msg}")
        return None

    explanation = payload.get("rule_explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        return None
    return explanation.strip()


def parse_compliance_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析合规检查结果（带Schema验证）"""
    if not payload:
        return None

    # 🔧 新增：Schema验证
    is_valid, error_msg = validate_agent_output("compliance_agent", payload)
    if not is_valid:
        logger.warning(f"Compliance agent output validation failed: {error_msg}")
        return None

    notes = payload.get("compliance_notes")
    reason = payload.get("manual_review_reason")
    if not isinstance(notes, list) or not all(isinstance(item, str) for item in notes):
        return None
    if not isinstance(reason, str) or not reason.strip():
        return None
    clean_notes = [item.strip() for item in notes if item.strip()]
    return {
        "compliance_notes": clean_notes,
        "manual_review_reason": reason.strip(),
    }


def parse_evidence_summary(payload: JSONDict | None) -> str | None:
    """解析证据摘要"""
    if not payload:
        return None
    summary = payload.get("evidence_summary")
    if not isinstance(summary, str) or not summary.strip():
        return None
    return summary.strip()


def parse_report_payload(payload: JSONDict | None) -> dict[str, str] | None:
    """解析报告内容"""
    if not payload:
        return None
    summary = payload.get("summary")
    suggestion = payload.get("suggestion")
    if not isinstance(summary, str) or not summary.strip():
        return None
    if not isinstance(suggestion, str) or not suggestion.strip():
        return None
    return {"summary": summary.strip(), "suggestion": suggestion.strip()}


def parse_fraud_detection_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析欺诈检测结果"""
    if not payload:
        return None
    fraud_indicators = payload.get("fraud_indicators")
    anomaly_score = payload.get("anomaly_score")
    fraud_type = payload.get("fraud_type")
    confidence = payload.get("confidence")

    if not isinstance(fraud_indicators, list) or not all(isinstance(item, str) for item in fraud_indicators):
        return None
    if not isinstance(anomaly_score, int) or not (0 <= anomaly_score <= 100):
        return None
    if not isinstance(fraud_type, str) or fraud_type not in ["account_takeover", "card_testing", "clean", "suspicious"]:
        return None
    if not isinstance(confidence, str) or confidence not in ["low", "medium", "high"]:
        return None

    return {
        "fraud_indicators": [item.strip() for item in fraud_indicators if item.strip()],
        "anomaly_score": anomaly_score,
        "fraud_type": fraud_type,
        "confidence": confidence,
    }


def parse_merchant_risk_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析商户风险结果"""
    if not payload:
        return None
    merchant_risk_factors = payload.get("merchant_risk_factors")
    merchant_reputation_score = payload.get("merchant_reputation_score")
    high_risk_category = payload.get("high_risk_category")
    recommendation = payload.get("recommendation")

    if not isinstance(merchant_risk_factors, list) or not all(isinstance(item, str) for item in merchant_risk_factors):
        return None
    if not isinstance(merchant_reputation_score, int) or not (0 <= merchant_reputation_score <= 100):
        return None
    if not isinstance(high_risk_category, bool):
        return None
    if not isinstance(recommendation, str) or not recommendation.strip():
        return None

    return {
        "merchant_risk_factors": [item.strip() for item in merchant_risk_factors if item.strip()],
        "merchant_reputation_score": merchant_reputation_score,
        "high_risk_category": high_risk_category,
        "recommendation": recommendation.strip(),
    }


def parse_device_fingerprint_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析设备指纹结果"""
    if not payload:
        return None
    device_risk_signals = payload.get("device_risk_signals")
    device_trust_score = payload.get("device_trust_score")
    is_emulator = payload.get("is_emulator")
    is_vpn_proxy = payload.get("is_vpn_proxy")
    device_reputation = payload.get("device_reputation")

    if not isinstance(device_risk_signals, list) or not all(isinstance(item, str) for item in device_risk_signals):
        return None
    if not isinstance(device_trust_score, int) or not (0 <= device_trust_score <= 100):
        return None
    if not isinstance(is_emulator, bool):
        return None
    if not isinstance(is_vpn_proxy, bool):
        return None
    if not isinstance(device_reputation, str) or device_reputation not in ["trusted", "neutral", "suspicious", "malicious"]:
        return None

    return {
        "device_risk_signals": [item.strip() for item in device_risk_signals if item.strip()],
        "device_trust_score": device_trust_score,
        "is_emulator": is_emulator,
        "is_vpn_proxy": is_vpn_proxy,
        "device_reputation": device_reputation,
    }


def parse_velocity_check_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析速度检查结果"""
    if not payload:
        return None
    velocity_violations = payload.get("velocity_violations")
    velocity_risk_score = payload.get("velocity_risk_score")
    burst_detected = payload.get("burst_detected")
    time_pattern_anomaly = payload.get("time_pattern_anomaly")
    recommendation = payload.get("recommendation")

    if not isinstance(velocity_violations, list) or not all(isinstance(item, str) for item in velocity_violations):
        return None
    if not isinstance(velocity_risk_score, int) or not (0 <= velocity_risk_score <= 100):
        return None
    if not isinstance(burst_detected, bool):
        return None
    if not isinstance(time_pattern_anomaly, bool):
        return None
    if not isinstance(recommendation, str) or not recommendation.strip():
        return None

    return {
        "velocity_violations": [item.strip() for item in velocity_violations if item.strip()],
        "velocity_risk_score": velocity_risk_score,
        "burst_detected": burst_detected,
        "time_pattern_anomaly": time_pattern_anomaly,
        "recommendation": recommendation.strip(),
    }
