"""
API 测试用例 - 审计接口

测试覆盖：
1. 成功场景
2. 认证失败
3. 输入验证
4. 安全防护
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 测试数据
VALID_API_KEY = "test-api-key-12345"
VALID_TRANSACTION = {
    "transaction_id": "TX_TEST_001",
    "amount": 1000.00,
    "user_id": "user_123",
    "merchant_id": "merchant_456",
    "timestamp": "2026-07-10T10:00:00Z",
    "payment_method": "credit_card",
    "description": "Test transaction"
}


class TestAuditAPI:
    """审计API测试套件"""

    def test_audit_transaction_success(self, monkeypatch):
        """测试: 成功审计交易"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.post(
            "/api/audit/transaction",
            headers={"X-API-Key": VALID_API_KEY},
            json=VALID_TRANSACTION
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "risk_score" in data["data"]
        assert "risk_level" in data["data"]
        assert 0 <= data["data"]["risk_score"] <= 100

    def test_audit_transaction_missing_api_key(self):
        """测试: 缺少API Key"""
        response = client.post(
            "/api/audit/transaction",
            json=VALID_TRANSACTION
        )

        assert response.status_code in [401, 503]

    def test_audit_transaction_invalid_api_key(self, monkeypatch):
        """测试: 无效API Key"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.post(
            "/api/audit/transaction",
            headers={"X-API-Key": "invalid-key"},
            json=VALID_TRANSACTION
        )

        assert response.status_code == 401

    def test_audit_transaction_invalid_amount(self, monkeypatch):
        """测试: 无效金额（负数）"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        invalid_tx = VALID_TRANSACTION.copy()
        invalid_tx["amount"] = -100

        response = client.post(
            "/api/audit/transaction",
            headers={"X-API-Key": VALID_API_KEY},
            json=invalid_tx
        )

        assert response.status_code in [400, 422]

    def test_audit_transaction_sql_injection_protection(self, monkeypatch):
        """测试: SQL注入防护"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        malicious_tx = VALID_TRANSACTION.copy()
        malicious_tx["transaction_id"] = "TX'; DROP TABLE audit_reports; --"

        response = client.post(
            "/api/audit/transaction",
            headers={"X-API-Key": VALID_API_KEY},
            json=malicious_tx
        )

        # 应该被安全验证拒绝或清洗
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            data = response.json()
            # 验证transaction_id被清洗
            assert "DROP" not in data["data"]["transaction_id"]

    def test_get_audit_report_success(self, monkeypatch):
        """测试: 成功获取审计报告"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        # 先创建审计记录
        create_response = client.post(
            "/api/audit/transaction",
            headers={"X-API-Key": VALID_API_KEY},
            json=VALID_TRANSACTION
        )

        assert create_response.status_code == 200

        # 查询报告
        response = client.get(
            f"/api/audit/report/{VALID_TRANSACTION['transaction_id']}",
            headers={"X-API-Key": VALID_API_KEY}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_audit_report_not_found(self, monkeypatch):
        """测试: 报告不存在"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.get(
            "/api/audit/report/NON_EXISTENT_TX",
            headers={"X-API-Key": VALID_API_KEY}
        )

        assert response.status_code == 404


class TestHealthAPI:
    """健康检查API测试"""

    def test_health_check(self):
        """测试: 健康检查"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# Pytest配置
@pytest.fixture(autouse=True)
def reset_db():
    """每个测试前重置数据库"""
    from app.db.database import init_db
    init_db()
    yield
