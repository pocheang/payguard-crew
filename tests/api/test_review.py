"""
审核工作流API测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_API_KEY = "test-api-key-12345"


class TestReviewAPI:
    """审核工作流测试套件"""

    def test_create_review(self, monkeypatch):
        """测试: 创建审核记录"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.post(
            "/api/review/create",
            headers={"X-API-Key": VALID_API_KEY},
            json={
                "transaction_id": "TX_REVIEW_001",
                "priority": "normal",
                "auto_assign": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_pending_reviews(self, monkeypatch):
        """测试: 查询待审核列表"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.get(
            "/api/review/list/pending",
            headers={"X-API-Key": VALID_API_KEY}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_review_statistics(self, monkeypatch):
        """测试: 获取审核统计"""
        monkeypatch.setenv("API_KEYS", VALID_API_KEY)

        response = client.get(
            "/api/review/statistics",
            headers={"X-API-Key": VALID_API_KEY}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
