"""
Core fallback functions for transaction, compliance, and report generation
"""
from app.schemas.transaction import TransactionInput


def build_transaction_findings(tx: TransactionInput) -> list[str]:
    """构建交易发现（本地逻辑）"""
    findings: list[str] = []
    if tx.account_age_days < 7:
        findings.append("新账号处于观察期内。")
    if tx.transaction_frequency_1h > 10:
        findings.append("近 1 小时交易频次偏高。")
    if tx.ip_location_status == "abnormal":
        findings.append("IP 地理位置存在异常。")
    if tx.device_status == "abnormal":
        findings.append("设备状态异常。")
    if tx.amount > 5000:
        findings.append("本笔交易金额较高。")
    if not findings:
        findings.append("未发现明显行为异常。")
    return findings


def build_compliance_notes(tx: TransactionInput, rule_result: dict) -> list[str]:
    """构建合规注释（本地逻辑）"""
    notes: list[str] = []
    if tx.kyc_status != "verified":
        notes.append("KYC 未完成完全认证。")
    if tx.is_blacklisted:
        notes.append("命中黑名单，应直接拦截。")
    if rule_result["requires_manual_review"]:
        notes.append("规则结果要求进入人工复核。")
    if not notes:
        notes.append("合规侧未发现额外人工复核触发项。")
    return notes


def build_fallback_summary(
    rule_result: dict,
    transaction_findings: list[str],
    compliance_notes: list[str],
    evidence_summary: str | None,
) -> str:
    """构建后备摘要"""
    rule_names = [rule["rule_name"] for rule in rule_result["triggered_rules"]]
    joined_rules = "、".join(rule_names) if rule_names else "无明显高风险规则"
    summary = (
        f"规则引擎命中 {len(rule_names)} 条规则（{joined_rules}），"
        f"交易特征包括：{'；'.join(transaction_findings)} "
        f"合规观察：{'；'.join(compliance_notes)}"
    )
    if evidence_summary:
        summary = f"{summary} 证据依据：{evidence_summary}"
    return summary


def build_fallback_suggestion(rule_result: dict) -> str:
    """构建后备建议"""
    if rule_result["decision"] == "reject":
        return "建议拒绝交易并保留完整审计记录。"
    if rule_result["risk_level"] == "high":
        return "建议暂缓交易并转人工复核。"
    if rule_result["risk_level"] == "medium":
        return "建议进入人工复核或二次校验流程。"
    return "建议自动通过，并保留基础审计记录。"
