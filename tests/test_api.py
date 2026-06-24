import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

REPORT_COLUMNS = [
    "id",
    "transaction_id",
    "user_id",
    "merchant_id",
    "risk_score",
    "risk_level",
    "decision",
    "summary",
    "suggestion",
    "requires_manual_review",
    "created_at",
]

LOG_COLUMNS = [
    "id",
    "transaction_id",
    "agent_name",
    "input_data",
    "output_data",
    "status",
    "error_message",
    "latency_ms",
    "created_at",
]

RULE_COLUMNS = [
    "id",
    "transaction_id",
    "rule_id",
    "rule_name",
    "reason",
    "score",
    "created_at",
]


def _load_sample_transaction() -> dict:
    sample_path = Path(__file__).resolve().parent.parent / "data" / "sample_transaction.json"
    return json.loads(sample_path.read_text(encoding="utf-8"))



def _table_columns(db_path: str, table_name: str) -> list[str]:
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row[1] for row in rows]



def test_audit_transaction_persists_report_and_logs(client) -> None:
    payload = _load_sample_transaction()

    response = client.post("/audit/transaction", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["transaction_id"] == payload["transaction_id"]
    assert body["risk_level"] == "high"
    assert body["requires_manual_review"] is True

    db_path = str(get_settings().db_path)
    assert _table_columns(db_path, "audit_reports") == REPORT_COLUMNS
    assert _table_columns(db_path, "audit_logs") == LOG_COLUMNS
    assert _table_columns(db_path, "rule_hits") == RULE_COLUMNS

    report_response = client.get(f"/audit/report/{payload['transaction_id']}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["transaction_id"] == payload["transaction_id"]
    assert report["user_id"] == payload["user_id"]
    assert report["merchant_id"] == payload["merchant_id"]
    assert report["created_at"].endswith("+00:00")
    assert len(report["triggered_rules"]) >= 1

    logs_response = client.get(f"/audit/logs/{payload['transaction_id']}")
    assert logs_response.status_code == 200
    logs = logs_response.json()["logs"]
    assert len(logs) >= 5
    assert logs[0]["agent_name"] == "transaction_agent"
    assert logs[0]["input_data"] is not None
    assert logs[0]["output_data"] is not None
    assert logs[0]["status"] == "completed"



def test_crewai_failure_falls_back_to_local_workflow(monkeypatch) -> None:
    from app.crew import audit_crew

    payload = _load_sample_transaction()

    # 使用项目内的测试目录
    test_db_dir = Path(__file__).parent / "test_data"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db_path = test_db_dir / "payguard-crewai-fallback.db"

    monkeypatch.setenv("SQLITE_DB_PATH", str(test_db_path))
    monkeypatch.setenv(
        "PAYGUARD_DOCS_DIR",
        str((Path(__file__).resolve().parent.parent / "docs").resolve()),
    )
    monkeypatch.setenv("ENABLE_CREWAI", "true")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    get_settings.cache_clear()

    def fake_crewai_task(*args, **kwargs):
        return None, 1, "forced CrewAI failure"

    monkeypatch.setattr(audit_crew, "_run_crewai_json_task", fake_crewai_task)
    monkeypatch.setattr(audit_crew, "generate_audit_narrative", lambda context: None)

    with TestClient(app) as test_client:
        response = test_client.post("/audit/transaction", json=payload)
        assert response.status_code == 200

        logs_response = test_client.get(f"/audit/logs/{payload['transaction_id']}")
        assert logs_response.status_code == 200
        logs = logs_response.json()["logs"]
        assert any(log["status"] == "fallback" for log in logs)
        assert any(log["error_message"] == "forced CrewAI failure" for log in logs)
        report_log = next(log for log in logs if log["agent_name"] == "report_agent")
        assert "\"backend\": \"local\"" in report_log["output_data"]

    get_settings.cache_clear()
    # 不删除数据库文件，避免权限问题



def test_missing_report_returns_404(client) -> None:
    response = client.get("/audit/report/DOES_NOT_EXIST")
    assert response.status_code == 404



def test_missing_logs_return_404(client) -> None:
    response = client.get("/audit/logs/DOES_NOT_EXIST")
    assert response.status_code == 404


def test_health_check_returns_ok(client) -> None:
    """测试：/health 返回 ok"""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body


def test_audit_transaction_returns_200(client) -> None:
    """测试：POST /audit/transaction 返回 200"""
    payload = _load_sample_transaction()
    response = client.post("/audit/transaction", json=payload)
    assert response.status_code == 200


def test_audit_response_has_required_fields(client) -> None:
    """测试：返回字段符合 AuditResponse"""
    payload = _load_sample_transaction()
    response = client.post("/audit/transaction", json=payload)
    assert response.status_code == 200

    body = response.json()
    # 验证所有必需字段存在
    assert "transaction_id" in body
    assert "risk_level" in body
    assert "risk_score" in body
    assert "decision" in body
    assert "summary" in body
    assert "triggered_rules" in body
    assert "evidence" in body
    assert "suggestion" in body
    assert "requires_manual_review" in body

    # 验证字段类型
    assert isinstance(body["transaction_id"], str)
    assert body["risk_level"] in ["low", "medium", "high"]
    assert isinstance(body["risk_score"], int)
    assert body["decision"] in ["approve", "review", "hold", "reject"]
    assert isinstance(body["summary"], str)
    assert isinstance(body["triggered_rules"], list)
    assert isinstance(body["evidence"], list)
    assert isinstance(body["suggestion"], str)
    assert isinstance(body["requires_manual_review"], bool)


def test_high_risk_example_returns_high(client) -> None:
    """测试：high risk 示例返回 high"""
    high_risk_payload = {
        "transaction_id": "TX_HIGH_RISK_TEST",
        "user_id": "U_HIGH",
        "merchant_id": "M_HIGH",
        "amount": 9000,
        "currency": "CNY",
        "account_age_days": 2,  # 新账户
        "transaction_frequency_1h": 15,  # 高频
        "ip_location_status": "abnormal",  # IP异常
        "device_status": "abnormal",  # 设备异常
        "kyc_status": "basic_verified",  # KYC未完整
        "merchant_risk_level": "high",  # 高风险商户
        "is_blacklisted": False,
        "timestamp": "2026-06-23T10:30:00",
    }

    response = client.post("/audit/transaction", json=high_risk_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["risk_level"] == "high"
    assert body["risk_score"] >= 70
    assert body["decision"] in ["review", "reject"]
    assert body["requires_manual_review"] is True
