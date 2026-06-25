"""
测试新增的4个Agent功能

运行方式:
python test_new_agents.py
"""
from app.schemas.transaction import TransactionInput
from app.crew.fallbacks import (
    build_fraud_detection_result,
    build_merchant_risk_result,
    build_device_fingerprint_result,
    build_velocity_check_result,
)
from datetime import datetime


def test_fraud_detection():
    """测试欺诈检测Agent"""
    print("\n=== 测试 Fraud Detection Agent ===")
    
    # 模拟高风险交易
    tx = TransactionInput(
        transaction_id="TEST001",
        user_id="U99999",
        merchant_id="M2033",
        amount=9800,
        currency="CNY",
        account_age_days=2,
        transaction_frequency_1h=25,
        ip_location_status="abnormal",
        device_status="abnormal",
        kyc_status="unverified",
        merchant_risk_level="high",
        is_blacklisted=False,
        timestamp=datetime.now(),
    )
    
    result = build_fraud_detection_result(tx)
    print(f"欺诈指标: {result['fraud_indicators']}")
    print(f"异常评分: {result['anomaly_score']}/100")
    print(f"欺诈类型: {result['fraud_type']}")
    print(f"置信度: {result['confidence']}")


def test_merchant_risk():
    """测试商户风险Agent"""
    print("\n=== 测试 Merchant Risk Agent ===")
    
    tx = TransactionInput(
        transaction_id="TEST002",
        user_id="U10086",
        merchant_id="M999001",  # 高风险商户前缀
        amount=5000,
        currency="CNY",
        account_age_days=100,
        transaction_frequency_1h=3,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="high",
        is_blacklisted=False,
        timestamp=datetime.now(),
    )
    
    result = build_merchant_risk_result(tx)
    print(f"商户风险因素: {result['merchant_risk_factors']}")
    print(f"商户声誉评分: {result['merchant_reputation_score']}/100")
    print(f"高风险类别: {result['high_risk_category']}")
    print(f"建议: {result['recommendation']}")


def test_device_fingerprint():
    """测试设备指纹Agent"""
    print("\n=== 测试 Device Fingerprint Agent ===")
    
    tx = TransactionInput(
        transaction_id="TEST003",
        user_id="U10086",
        merchant_id="M2033",
        amount=1000,
        currency="CNY",
        account_age_days=50,
        transaction_frequency_1h=5,
        ip_location_status="abnormal",
        device_status="abnormal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp=datetime.now(),
    )
    
    result = build_device_fingerprint_result(tx)
    print(f"设备风险信号: {result['device_risk_signals']}")
    print(f"设备信任评分: {result['device_trust_score']}/100")
    print(f"是否模拟器: {result['is_emulator']}")
    print(f"是否VPN/代理: {result['is_vpn_proxy']}")
    print(f"设备声誉: {result['device_reputation']}")


def test_velocity_check():
    """测试速度检查Agent"""
    print("\n=== 测试 Velocity Check Agent ===")
    
    tx = TransactionInput(
        transaction_id="TEST004",
        user_id="U10086",
        merchant_id="M2033",
        amount=15000,
        currency="CNY",
        account_age_days=3,
        transaction_frequency_1h=22,  # 极高频率
        ip_location_status="normal",
        device_status="normal",
        kyc_status="basic_verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp=datetime.now(),
    )
    
    result = build_velocity_check_result(tx)
    print(f"速度违规: {result['velocity_violations']}")
    print(f"速度风险评分: {result['velocity_risk_score']}/100")
    print(f"突发检测: {result['burst_detected']}")
    print(f"时间模式异常: {result['time_pattern_anomaly']}")
    print(f"建议: {result['recommendation']}")


if __name__ == "__main__":
    print("=" * 60)
    print("PayGuard Crew v0.1.2 - 新增Agent功能测试")
    print("=" * 60)
    
    test_fraud_detection()
    test_merchant_risk()
    test_device_fingerprint()
    test_velocity_check()
    
    print("\n" + "=" * 60)
    print("测试完成！所有4个新Agent运行正常 ✅")
    print("=" * 60)
