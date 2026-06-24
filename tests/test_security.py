"""安全相关测试"""
import pytest
from fastapi import HTTPException

from app.auth.api_key import get_valid_api_keys, verify_api_key


def test_get_valid_api_keys_empty(monkeypatch):
    """测试未配置 API Keys"""
    monkeypatch.setenv("API_KEYS", "")
    keys = get_valid_api_keys()
    assert keys == set()


def test_get_valid_api_keys_single(monkeypatch):
    """测试单个 API Key"""
    monkeypatch.setenv("API_KEYS", "test-key-123")
    keys = get_valid_api_keys()
    assert keys == {"test-key-123"}


def test_get_valid_api_keys_multiple(monkeypatch):
    """测试多个 API Keys"""
    monkeypatch.setenv("API_KEYS", "key1,key2,key3")
    keys = get_valid_api_keys()
    assert keys == {"key1", "key2", "key3"}


def test_get_valid_api_keys_with_spaces(monkeypatch):
    """测试带空格的 API Keys"""
    monkeypatch.setenv("API_KEYS", " key1 , key2 , key3 ")
    keys = get_valid_api_keys()
    assert keys == {"key1", "key2", "key3"}


def test_verify_api_key_no_config_allows_access(monkeypatch):
    """测试未配置 API Keys 时允许访问（开发模式）"""
    monkeypatch.setenv("API_KEYS", "")

    # 模拟 Security dependency
    result = verify_api_key(None)
    assert result == "dev-mode"


def test_verify_api_key_missing_key_raises_401(monkeypatch):
    """测试缺少 API Key 返回 401"""
    monkeypatch.setenv("API_KEYS", "valid-key")

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(None)

    assert exc_info.value.status_code == 401
    assert "缺少 API Key" in exc_info.value.detail


def test_verify_api_key_invalid_key_raises_401(monkeypatch):
    """测试无效 API Key 返回 401"""
    monkeypatch.setenv("API_KEYS", "valid-key")

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("invalid-key")

    assert exc_info.value.status_code == 401
    assert "无效的 API Key" in exc_info.value.detail


def test_verify_api_key_valid_key_returns_key(monkeypatch):
    """测试有效 API Key 返回该 Key"""
    monkeypatch.setenv("API_KEYS", "valid-key-123")

    result = verify_api_key("valid-key-123")
    assert result == "valid-key-123"


def test_sql_injection_protection():
    """测试 SQL 注入防护"""
    from app.db.database import ALLOWED_TABLES

    # 验证白名单
    assert "audit_reports" in ALLOWED_TABLES
    assert "audit_logs" in ALLOWED_TABLES
    assert "rule_hits" in ALLOWED_TABLES

    # 确保只有这三个表
    assert len(ALLOWED_TABLES) == 3


def test_transaction_input_validation():
    """测试交易输入验证"""
    from app.schemas.transaction import TransactionInput
    from pydantic import ValidationError

    # 测试超大金额被拒绝
    with pytest.raises(ValidationError):
        TransactionInput(
            transaction_id="TX001",
            user_id="U001",
            merchant_id="M001",
            amount=9999999999.99,  # 超过限制
            currency="CNY",
            account_age_days=10,
            transaction_frequency_1h=5,
            ip_location_status="normal",
            device_status="normal",
            kyc_status="verified",
            merchant_risk_level="low",
            is_blacklisted=False,
            timestamp="2026-06-24T10:00:00"
        )

    # 测试无效的 transaction_id 格式
    with pytest.raises(ValidationError):
        TransactionInput(
            transaction_id="TX001; DROP TABLE users;",  # 包含特殊字符
            user_id="U001",
            merchant_id="M001",
            amount=1000,
            currency="CNY",
            account_age_days=10,
            transaction_frequency_1h=5,
            ip_location_status="normal",
            device_status="normal",
            kyc_status="verified",
            merchant_risk_level="low",
            is_blacklisted=False,
            timestamp="2026-06-24T10:00:00"
        )

    # 测试有效的输入
    valid_input = TransactionInput(
        transaction_id="TX001",
        user_id="U001",
        merchant_id="M001",
        amount=5000.00,
        currency="CNY",
        account_age_days=10,
        transaction_frequency_1h=5,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-24T10:00:00"
    )

    assert valid_input.amount == 5000.00
    assert valid_input.transaction_id == "TX001"


def test_account_age_validation():
    """测试账户年龄验证"""
    from app.schemas.transaction import TransactionInput
    from pydantic import ValidationError

    # 测试超大账户年龄被拒绝
    with pytest.raises(ValidationError):
        TransactionInput(
            transaction_id="TX001",
            user_id="U001",
            merchant_id="M001",
            amount=1000,
            currency="CNY",
            account_age_days=99999,  # 超过100年
            transaction_frequency_1h=5,
            ip_location_status="normal",
            device_status="normal",
            kyc_status="verified",
            merchant_risk_level="low",
            is_blacklisted=False,
            timestamp="2026-06-24T10:00:00"
        )


def test_transaction_frequency_validation():
    """测试交易频率验证"""
    from app.schemas.transaction import TransactionInput
    from pydantic import ValidationError

    # 测试超高频率被拒绝
    with pytest.raises(ValidationError):
        TransactionInput(
            transaction_id="TX001",
            user_id="U001",
            merchant_id="M001",
            amount=1000,
            currency="CNY",
            account_age_days=10,
            transaction_frequency_1h=9999,  # 超过1000
            ip_location_status="normal",
            device_status="normal",
            kyc_status="verified",
            merchant_risk_level="low",
            is_blacklisted=False,
            timestamp="2026-06-24T10:00:00"
        )
