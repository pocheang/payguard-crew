"""
Tests for database operations
"""
from pathlib import Path

import pytest

from app.config import get_settings
from app.db.repository import (
    get_audit_logs,
    get_audit_report,
    save_audit_log,
    save_audit_report,
    save_rule_hits,
)
from app.schemas.audit import AuditLogEntry, AuditResponse, TriggeredRule
from app.schemas.transaction import TransactionInput


@pytest.fixture
def test_db_path(monkeypatch: pytest.MonkeyPatch) -> Path:
    """创建测试数据库路径"""
    db_path = Path(__file__).parent / "test_data" / "test.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("SQLITE_DB_PATH", str(db_path))
    monkeypatch.setenv(
        "PAYGUARD_DOCS_DIR",
        str((Path(__file__).resolve().parent.parent / "docs").resolve()),
    )
    get_settings.cache_clear()
    yield db_path
    get_settings.cache_clear()
    # 不删除数据库文件，避免权限问题


@pytest.fixture
def sample_transaction() -> TransactionInput:
    """创建示例交易"""
    return TransactionInput(
        transaction_id="TX_DB_TEST_001",
        user_id="U_TEST",
        merchant_id="M_TEST",
        amount=5000,
        currency="CNY",
        account_age_days=30,
        transaction_frequency_1h=3,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )


@pytest.fixture
def sample_audit_response() -> AuditResponse:
    """创建示例审计响应"""
    return AuditResponse(
        transaction_id="TX_DB_TEST_001",
        risk_level="medium",
        risk_score=35,
        decision="review",
        summary="测试交易，需要人工复核",
        triggered_rules=[
            TriggeredRule(
                rule_id="R001",
                rule_name="test_rule",
                reason="测试规则触发",
                score=35,
            )
        ],
        evidence=[],
        suggestion="建议人工复核",
        requires_manual_review=True,
    )


def test_save_audit_report(
    test_db_path: Path,
    sample_transaction: TransactionInput,
    sample_audit_response: AuditResponse,
) -> None:
    """测试：保存报告"""
    # 保存报告
    save_audit_report(sample_transaction, sample_audit_response)

    # 验证数据库文件已创建
    assert test_db_path.exists(), "Database file should be created"


def test_get_audit_report(
    test_db_path: Path,
    sample_transaction: TransactionInput,
    sample_audit_response: AuditResponse,
) -> None:
    """测试：查询报告"""
    # 先保存报告
    save_audit_report(sample_transaction, sample_audit_response)
    save_rule_hits(
        sample_audit_response.transaction_id,
        [rule.model_dump() for rule in sample_audit_response.triggered_rules],
    )

    # 查询报告
    report = get_audit_report(sample_audit_response.transaction_id)

    assert report is not None, "Should retrieve the saved report"
    assert report.transaction_id == sample_audit_response.transaction_id
    assert report.user_id == sample_transaction.user_id
    assert report.merchant_id == sample_transaction.merchant_id
    assert report.risk_level == sample_audit_response.risk_level
    assert report.risk_score == sample_audit_response.risk_score
    assert report.decision == sample_audit_response.decision
    assert report.requires_manual_review == sample_audit_response.requires_manual_review
    assert len(report.triggered_rules) == len(sample_audit_response.triggered_rules)


def test_get_nonexistent_report(test_db_path: Path) -> None:
    """测试：查询不存在的报告返回 None"""
    report = get_audit_report("NONEXISTENT_TX")
    assert report is None, "Should return None for nonexistent report"


def test_save_audit_log(test_db_path: Path) -> None:
    """测试：保存日志"""
    log_entry = AuditLogEntry(
        agent_name="test_agent",
        input_data="test input",
        output_data="test output",
        status="completed",
        error_message=None,
        latency_ms=100,
    )

    # 保存日志
    save_audit_log("TX_LOG_TEST", log_entry)

    # 验证数据库文件已创建
    assert test_db_path.exists(), "Database file should be created"


def test_get_audit_logs(test_db_path: Path) -> None:
    """测试：查询日志"""
    import uuid
    transaction_id = f"TX_LOGS_TEST_{uuid.uuid4().hex[:8]}"

    # 保存多条日志
    logs = [
        AuditLogEntry(
            agent_name="agent_1",
            input_data="input 1",
            output_data="output 1",
            status="completed",
            latency_ms=50,
        ),
        AuditLogEntry(
            agent_name="agent_2",
            input_data="input 2",
            output_data="output 2",
            status="completed",
            latency_ms=75,
        ),
        AuditLogEntry(
            agent_name="agent_3",
            input_data="input 3",
            output_data=None,
            status="failed",
            error_message="test error",
            latency_ms=25,
        ),
    ]

    for log in logs:
        save_audit_log(transaction_id, log)

    # 查询日志
    log_response = get_audit_logs(transaction_id)

    assert log_response.transaction_id == transaction_id
    assert len(log_response.logs) == 3

    # 验证日志顺序和内容
    assert log_response.logs[0].agent_name == "agent_1"
    assert log_response.logs[1].agent_name == "agent_2"
    assert log_response.logs[2].agent_name == "agent_3"
    assert log_response.logs[2].status == "failed"
    assert log_response.logs[2].error_message == "test error"


def test_get_logs_for_nonexistent_transaction(test_db_path: Path) -> None:
    """测试：查询不存在的交易日志返回空列表"""
    log_response = get_audit_logs("NONEXISTENT_TX")
    assert log_response.transaction_id == "NONEXISTENT_TX"
    assert log_response.logs == [], "Should return empty list for nonexistent transaction"


def test_save_rule_hits(test_db_path: Path) -> None:
    """测试：保存规则命中记录"""
    transaction_id = "TX_RULES_TEST"
    triggered_rules = [
        {
            "rule_id": "R001",
            "rule_name": "test_rule_1",
            "reason": "测试原因1",
            "score": 25,
        },
        {
            "rule_id": "R002",
            "rule_name": "test_rule_2",
            "reason": "测试原因2",
            "score": 20,
        },
    ]

    # 保存规则命中记录
    save_rule_hits(transaction_id, triggered_rules)

    # 通过查询报告来验证规则保存成功
    # 注意：需要先创建报告记录
    from app.schemas.audit import AuditResponse

    test_report = AuditResponse(
        transaction_id=transaction_id,
        risk_level="medium",
        risk_score=45,
        decision="review",
        summary="测试",
        triggered_rules=[
            TriggeredRule(**rule) for rule in triggered_rules
        ],
        evidence=[],
        suggestion="测试建议",
        requires_manual_review=True,
    )

    from app.schemas.transaction import TransactionInput

    test_tx = TransactionInput(
        transaction_id=transaction_id,
        user_id="U_TEST",
        merchant_id="M_TEST",
        amount=1000,
        currency="CNY",
        account_age_days=10,
        transaction_frequency_1h=1,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp="2026-06-23T10:30:00",
    )

    save_audit_report(test_tx, test_report)

    # 查询报告验证规则
    report = get_audit_report(transaction_id)
    assert report is not None
    assert len(report.triggered_rules) == 2
    assert report.triggered_rules[0].rule_id == "R001"
    assert report.triggered_rules[1].rule_id == "R002"
