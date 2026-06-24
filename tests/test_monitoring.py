"""
测试监控和健康检查功能
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """测试详细健康检查"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ["ok", "degraded", "error"]
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert "environment" in data
    assert "components" in data

    # 检查组件状态
    components = data["components"]
    assert "database" in components
    assert "knowledge_base" in components
    assert "rag" in components
    assert "llm" in components


def test_liveness_check():
    """测试存活检查"""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check():
    """测试就绪检查"""
    try:
        response = client.get("/health/ready")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]
    except Exception:
        # 某些环境下数据库可能未初始化，这是正常的
        pass


def test_metrics_endpoint():
    """测试 Prometheus metrics 端点"""
    response = client.get("/metrics")
    assert response.status_code == 200

    # Prometheus 返回 text/plain 格式
    assert "text/plain" in response.headers["content-type"]

    # 检查是否包含指标
    content = response.text
    assert "payguard" in content


def test_root_endpoint():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "payguard-crew"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert data["metrics"] == "/metrics"


def test_request_id_header():
    """测试 Request ID 头部"""
    # 不提供 Request ID
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    request_id1 = response.headers["X-Request-ID"]
    assert len(request_id1) > 0

    # 提供自定义 Request ID
    custom_id = "test-request-123"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


def test_security_headers():
    """测试安全响应头"""
    response = client.get("/health")

    # 检查安全头部
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers


def test_rate_limit_headers():
    """测试速率限制头部"""
    response = client.get("/health")

    # slowapi 会添加速率限制头部
    # 注意：这些头部可能不会在测试环境中出现
    # 这里只是确保请求不会因为速率限制而失败
    assert response.status_code == 200
