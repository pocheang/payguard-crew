from app.rules.risk_rules import evaluate_risk
from app.schemas.transaction import TransactionInput



def test_high_risk_transaction():
    tx = TransactionInput(
        transaction_id="TX_TEST",
        user_id="U1",
        merchant_id="M1",
        amount=9800,
        currency="CNY",
        account_age_days=3,
        transaction_frequency_1h=12,
        ip_location_status="abnormal",
        device_status="abnormal",
        kyc_status="basic_verified",
        merchant_risk_level="medium",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )
    result = evaluate_risk(tx)
    assert result["risk_level"] == "high"
    assert result["risk_score"] >= 70



def test_blacklist_transaction_is_rejected():
    tx = TransactionInput(
        transaction_id="TX_BLACKLIST",
        user_id="U2",
        merchant_id="M2",
        amount=10,
        currency="CNY",
        account_age_days=365,
        transaction_frequency_1h=1,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=True,
        timestamp="2026-06-23T10:30:00",
    )

    result = evaluate_risk(tx)

    assert result["decision"] == "reject"
    assert result["risk_level"] == "high"
    assert result["risk_score"] == 100
    assert result["requires_manual_review"] is True



def test_low_risk_transaction_is_approved():
    tx = TransactionInput(
        transaction_id="TX_LOW",
        user_id="U3",
        merchant_id="M3",
        amount=120,
        currency="CNY",
        account_age_days=600,
        transaction_frequency_1h=1,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )

    result = evaluate_risk(tx)

    assert result["decision"] == "approve"
    assert result["risk_level"] == "low"
    assert result["risk_score"] == 0


def test_high_frequency_triggers_r002():
    """测试：高频交易命中 R002"""
    tx = TransactionInput(
        transaction_id="TX_HIGH_FREQ",
        user_id="U4",
        merchant_id="M4",
        amount=500,
        currency="CNY",
        account_age_days=100,
        transaction_frequency_1h=15,  # 超过10次
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )

    result = evaluate_risk(tx)

    assert any(rule["rule_id"] == "R002" for rule in result["triggered_rules"])
    assert any(
        rule["rule_name"] == "high_frequency_transaction"
        for rule in result["triggered_rules"]
    )
    assert result["risk_score"] >= 20


def test_new_account_high_amount_triggers_r001():
    """测试：新账户大额交易命中 R001"""
    tx = TransactionInput(
        transaction_id="TX_NEW_HIGH",
        user_id="U5",
        merchant_id="M5",
        amount=6000,  # 超过5000
        currency="CNY",
        account_age_days=5,  # 小于7天
        transaction_frequency_1h=2,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )

    result = evaluate_risk(tx)

    assert any(rule["rule_id"] == "R001" for rule in result["triggered_rules"])
    assert any(
        rule["rule_name"] == "new_account_high_amount"
        for rule in result["triggered_rules"]
    )
    assert result["risk_score"] >= 25
