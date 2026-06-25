"""
Risk detection fallback functions - Fraud, Merchant, Device, Velocity
"""
from app.schemas.transaction import TransactionInput


def build_fraud_detection_result(tx: TransactionInput) -> dict:
    """构建欺诈检测结果（本地逻辑）"""
    fraud_indicators = []
    anomaly_score = 0

    # 账户接管模式检测
    if tx.device_status == "abnormal" and tx.ip_location_status == "abnormal":
        fraud_indicators.append("可疑的账户接管行为：设备和IP同时异常")
        anomaly_score += 30

    # 卡测试模式检测
    if tx.transaction_frequency_1h > 10 and tx.amount < 100:
        fraud_indicators.append("疑似卡测试行为：高频小额交易")
        anomaly_score += 25

    # 速度滥用检测
    if tx.transaction_frequency_1h > 15:
        fraud_indicators.append("异常交易速度：1小时内交易次数过多")
        anomaly_score += 20

    # 新账户欺诈
    if tx.account_age_days < 3 and tx.amount > 5000:
        fraud_indicators.append("新账户高额交易：典型欺诈模式")
        anomaly_score += 25

    if not fraud_indicators:
        fraud_indicators.append("未检测到明显欺诈模式")

    # 确定欺诈类型
    fraud_type = "clean"
    if anomaly_score >= 50:
        fraud_type = "account_takeover" if tx.device_status == "abnormal" else "suspicious"
    elif anomaly_score >= 25:
        fraud_type = "card_testing" if tx.transaction_frequency_1h > 10 else "suspicious"

    confidence = "high" if anomaly_score >= 50 else "medium" if anomaly_score >= 25 else "low"

    return {
        "fraud_indicators": fraud_indicators,
        "anomaly_score": min(anomaly_score, 100),
        "fraud_type": fraud_type,
        "confidence": confidence,
    }


def build_merchant_risk_result(tx: TransactionInput) -> dict:
    """构建商户风险结果（本地逻辑）"""
    merchant_risk_factors = []
    reputation_score = 0

    # 商户风险等级评估
    if tx.merchant_risk_level == "high":
        merchant_risk_factors.append("商户被标记为高风险类别")
        reputation_score += 40
    elif tx.merchant_risk_level == "medium":
        merchant_risk_factors.append("商户属于中风险类别")
        reputation_score += 20

    # 高风险行业检测
    high_risk_merchant_prefixes = ["M999", "M888", "M777"]
    if any(tx.merchant_id.startswith(prefix) for prefix in high_risk_merchant_prefixes):
        merchant_risk_factors.append("商户属于高风险行业（加密货币/博彩/成人内容）")
        reputation_score += 30

    if not merchant_risk_factors:
        merchant_risk_factors.append("商户风险评估正常")

    high_risk_category = reputation_score >= 40

    recommendation = (
        "建议暂停该商户交易，进行人工审核"
        if reputation_score >= 60
        else "建议加强监控，设置交易限额"
        if reputation_score >= 40
        else "商户风险可控，正常处理"
    )

    return {
        "merchant_risk_factors": merchant_risk_factors,
        "merchant_reputation_score": min(reputation_score, 100),
        "high_risk_category": high_risk_category,
        "recommendation": recommendation,
    }


def build_device_fingerprint_result(tx: TransactionInput) -> dict:
    """构建设备指纹结果（本地逻辑）"""
    device_risk_signals = []
    trust_score = 100
    is_emulator = False
    is_vpn_proxy = False

    if tx.device_status == "abnormal":
        device_risk_signals.append("设备指纹异常：可能使用模拟器或篡改设备")
        trust_score -= 30
        is_emulator = True

    if tx.ip_location_status == "abnormal":
        device_risk_signals.append("IP地址异常：疑似使用VPN或代理服务")
        trust_score -= 25
        is_vpn_proxy = True

    if tx.transaction_frequency_1h > 10:
        device_risk_signals.append("设备关联多个账户：可能是批量欺诈行为")
        trust_score -= 20

    if not device_risk_signals:
        device_risk_signals.append("设备指纹验证通过")

    device_reputation = (
        "trusted" if trust_score >= 70
        else "neutral" if trust_score >= 50
        else "suspicious" if trust_score >= 30
        else "malicious"
    )

    return {
        "device_risk_signals": device_risk_signals,
        "device_trust_score": max(trust_score, 0),
        "is_emulator": is_emulator,
        "is_vpn_proxy": is_vpn_proxy,
        "device_reputation": device_reputation,
    }


def build_velocity_check_result(tx: TransactionInput) -> dict:
    """构建速度检查结果（本地逻辑）"""
    velocity_violations = []
    velocity_risk_score = 0
    burst_detected = False
    time_pattern_anomaly = False

    if tx.transaction_frequency_1h > 20:
        velocity_violations.append("严重违反1小时交易频率限制（>20次）")
        velocity_risk_score += 40
        burst_detected = True
    elif tx.transaction_frequency_1h > 10:
        velocity_violations.append("超出1小时交易频率阈值（>10次）")
        velocity_risk_score += 25

    if tx.amount > 10000 and tx.transaction_frequency_1h > 5:
        velocity_violations.append("大额交易频率异常：1小时内多笔大额交易")
        velocity_risk_score += 30
        burst_detected = True

    if tx.account_age_days < 7 and tx.transaction_frequency_1h > 5:
        velocity_violations.append("新账户交易频率过高：可能是批量注册欺诈")
        velocity_risk_score += 25

    if tx.transaction_frequency_1h > 15:
        velocity_violations.append("交易时间模式异常：非正常交易时段高频交易")
        time_pattern_anomaly = True
        velocity_risk_score += 20

    if not velocity_violations:
        velocity_violations.append("交易速度正常")

    recommendation = (
        "建议立即冻结账户，疑似自动化攻击"
        if velocity_risk_score >= 70
        else "建议暂停交易，进行人工审核"
        if velocity_risk_score >= 40
        else "建议加强监控，设置交易间隔限制"
        if velocity_risk_score >= 20
        else "交易速度正常，无需额外措施"
    )

    return {
        "velocity_violations": velocity_violations,
        "velocity_risk_score": min(velocity_risk_score, 100),
        "burst_detected": burst_detected,
        "time_pattern_anomaly": time_pattern_anomaly,
        "recommendation": recommendation,
    }
