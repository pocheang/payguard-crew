"""
审计结果解析器
"""
from typing import Any

JSONDict = dict[str, Any]


def parse_transaction_findings(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析交易发现结果"""
    if not payload:
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
    """解析规则解释"""
    if not payload:
        return None
    explanation = payload.get("rule_explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        return None
    return explanation.strip()


def parse_compliance_result(payload: JSONDict | None) -> dict[str, Any] | None:
    """解析合规检查结果"""
    if not payload:
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
