"""
性能优化测试

测试优化后的审计流程性能
"""
import pytest
import asyncio
from app.crew.audit_crew import run_audit_crew, run_audit_crew_async
from app.schemas.transaction import TransactionInput
from datetime import datetime


def create_test_transaction() -> TransactionInput:
    """创建测试交易"""
    return TransactionInput(
        transaction_id="TEST_OPTIMIZED_001",
        user_id="U_TEST",
        merchant_id="M_TEST",
        amount=3000,
        currency="CNY",
        account_age_days=10,
        transaction_frequency_1h=5,
        ip_location_status="normal",
        device_status="normal",
        kyc_status="verified",
        merchant_risk_level="low",
        is_blacklisted=False,
        timestamp=datetime.now().isoformat()
    )


def test_optimized_audit_crew_sync():
    """测试同步版本（向后兼容）"""
    tx = create_test_transaction()

    import time
    start = time.time()
    result = run_audit_crew(tx)
    elapsed = (time.time() - start) * 1000

    # 验证结果
    assert result.transaction_id == tx.transaction_id
    assert result.risk_level in ["low", "medium", "high"]
    assert result.risk_score >= 0
    assert result.decision in ["approve", "review", "hold", "reject"]

    print(f"\nOK - Sync version elapsed: {elapsed:.0f}ms")


@pytest.mark.asyncio
async def test_optimized_audit_crew_async():
    """测试异步版本（优化版）"""
    tx = create_test_transaction()

    import time
    start = time.time()
    result = await run_audit_crew_async(tx)
    elapsed = (time.time() - start) * 1000

    # 验证结果
    assert result.transaction_id == tx.transaction_id
    assert result.risk_level in ["low", "medium", "high"]
    assert result.risk_score >= 0
    assert result.decision in ["approve", "review", "hold", "reject"]

    print(f"\nOK - Async version elapsed: {elapsed:.0f}ms")
    print(f"   Risk level: {result.risk_level}")
    print(f"   Risk score: {result.risk_score}")
    print(f"   Decision: {result.decision}")


def test_database_batch_insert():
    """测试批量插入性能"""
    from app.db.repository import save_audit_result_optimized
    from app.schemas.audit import AuditLogEntry, AuditResponse, TriggeredRule

    tx = create_test_transaction()

    # 创建测试数据
    response = AuditResponse(
        transaction_id=tx.transaction_id,
        risk_level="low",
        risk_score=0,
        decision="approve",
        summary="Test summary",
        triggered_rules=[
            TriggeredRule(
                rule_id="R001",
                rule_name="test_rule",
                reason="test reason",
                score=10
            )
        ],
        evidence=[],
        suggestion="Test suggestion",
        requires_manual_review=False
    )

    logs = [
        AuditLogEntry(
            agent_name=f"test_agent_{i}",
            input_data="{}",
            output_data="{}",
            status="completed",
            latency_ms=10,
            error_message=None,
            created_at=None
        )
        for i in range(5)
    ]

    import time
    start = time.time()
    save_audit_result_optimized(tx, response, logs)
    elapsed = (time.time() - start) * 1000

    print(f"\nOK - Batch insert elapsed: {elapsed:.0f}ms")
    assert elapsed < 100, "Batch insert should complete in 100ms"


def test_chromadb_warmup():
    """测试 ChromaDB 预热"""
    from app.rag.vector_store import get_vector_store

    import time

    # 第一次调用（可能需要加载）
    start = time.time()
    store1 = get_vector_store()
    first_call = (time.time() - start) * 1000

    # 第二次调用（应该很快）
    start = time.time()
    store2 = get_vector_store()
    second_call = (time.time() - start) * 1000

    print(f"\nOK - ChromaDB first call: {first_call:.0f}ms")
    print(f"OK - ChromaDB second call: {second_call:.0f}ms")

    assert second_call < first_call, "Warmed call should be faster"
    assert store1 is store2, "Should return same instance (cached)"


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 性能优化测试")
    print("=" * 60)

    # 测试批量写入
    print("\n1. 测试批量写入优化...")
    test_database_batch_insert()

    # 测试 ChromaDB 预热
    print("\n2. 测试 ChromaDB 预热...")
    test_chromadb_warmup()

    # 测试同步版本
    print("\n3. 测试同步版本...")
    test_optimized_audit_crew_sync()

    # 测试异步版本
    print("\n4. 测试异步版本...")
    asyncio.run(test_optimized_audit_crew_async())

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
