from app.schemas.transaction import TransactionInput


def _rule(rule_id: str, rule_name: str, reason: str, score: int) -> dict:
    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "reason": reason,
        "score": score,
    }


def evaluate_risk(tx: TransactionInput) -> dict:
    """
    Deterministic risk rule engine.

    Important design principle:
    - Hard risk rules should be executed by code.
    - LLM should only explain, summarize, and generate reports.
    """
    triggered_rules: list[dict] = []
    risk_score = 0

    if tx.is_blacklisted:
        triggered_rules.append(
            _rule("R007", "blacklist_hit", "用户、设备或商户命中黑名单", 100)
        )
        return {
            "risk_score": 100,
            "risk_level": "high",
            "decision": "reject",
            "triggered_rules": triggered_rules,
            "requires_manual_review": True,
        }

    if tx.account_age_days < 7 and tx.amount > 5000:
        triggered_rules.append(
            _rule("R001", "new_account_high_amount", "账户注册小于7天且交易金额超过5000", 25)
        )
        risk_score += 25

    if tx.transaction_frequency_1h > 10:
        triggered_rules.append(
            _rule("R002", "high_frequency_transaction", "1小时内交易次数超过10次", 20)
        )
        risk_score += 20

    if tx.ip_location_status == "abnormal":
        triggered_rules.append(
            _rule("R003", "abnormal_ip_location", "交易IP地区异常", 15)
        )
        risk_score += 15

    if tx.kyc_status != "verified" and tx.amount > 3000:
        triggered_rules.append(
            _rule("R004", "incomplete_kyc_high_amount", "KYC未完整认证且交易金额超过3000", 20)
        )
        risk_score += 20

    if tx.merchant_risk_level == "high":
        triggered_rules.append(
            _rule("R005", "high_risk_merchant", "商户风险等级为 high", 25)
        )
        risk_score += 25

    if tx.device_status == "abnormal":
        triggered_rules.append(
            _rule("R006", "abnormal_device", "交易设备状态异常", 15)
        )
        risk_score += 15

    # R008: 欺诈模式检测 - 账户接管
    if tx.device_status == "abnormal" and tx.ip_location_status == "abnormal":
        triggered_rules.append(
            _rule("R008", "account_takeover_pattern", "设备和IP同时异常，疑似账户接管", 30)
        )
        risk_score += 30

    # R009: 卡测试检测 - 高频小额交易
    if tx.transaction_frequency_1h > 10 and tx.amount < 100:
        triggered_rules.append(
            _rule("R009", "card_testing_pattern", "高频小额交易，疑似卡测试", 25)
        )
        risk_score += 25

    # R010: 速度滥用 - 极高频率
    if tx.transaction_frequency_1h > 20:
        triggered_rules.append(
            _rule("R010", "velocity_abuse", "1小时内交易超过20次，严重违反速度限制", 35)
        )
        risk_score += 35

    # R011: 高风险商户行业 - 通过商户ID前缀识别
    high_risk_prefixes = ["M999", "M888", "M777"]
    if any(tx.merchant_id.startswith(prefix) for prefix in high_risk_prefixes):
        triggered_rules.append(
            _rule("R011", "high_risk_industry", "商户属于高风险行业（加密/博彩/成人）", 30)
        )
        risk_score += 30

    # R012: 新账户速度滥用
    if tx.account_age_days < 7 and tx.transaction_frequency_1h > 5:
        triggered_rules.append(
            _rule("R012", "new_account_velocity", "新账户高频交易，疑似批量欺诈", 25)
        )
        risk_score += 25

    # R013: 大额交易频率异常
    if tx.amount > 10000 and tx.transaction_frequency_1h > 3:
        triggered_rules.append(
            _rule("R013", "large_amount_frequency", "短时间内多笔大额交易", 30)
        )
        risk_score += 30

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "high"
        decision = "review"
        requires_manual_review = True
    elif risk_score >= 30:
        risk_level = "medium"
        decision = "review"
        requires_manual_review = True
    else:
        risk_level = "low"
        decision = "approve"
        requires_manual_review = False

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "triggered_rules": triggered_rules,
        "requires_manual_review": requires_manual_review,
    }


def build_rule_query(triggered_rules: list[dict], tx: TransactionInput) -> str:
    names = " ".join(rule["rule_name"] for rule in triggered_rules)
    return (
        f"{names} amount {tx.amount} account_age_days {tx.account_age_days} "
        f"kyc {tx.kyc_status} ip {tx.ip_location_status} device {tx.device_status} "
        f"merchant {tx.merchant_risk_level}"
    )
