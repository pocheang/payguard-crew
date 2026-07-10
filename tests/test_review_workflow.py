"""
后端单元测试 - 审核工作流
"""
import pytest
from datetime import datetime, timedelta
from app.services.review_service_enhanced import (
    create_review_record,
    get_review_record,
    update_review_status,
    list_pending_reviews,
    get_review_statistics,
    auto_assign_reviewer,
    get_reviewer_workload,
    ReviewStatus,
)


class TestReviewWorkflow:
    """审核工作流测试"""

    def setup_method(self):
        """每个测试前清空数据"""
        from app.services import review_service_enhanced
        review_service_enhanced.review_records.clear()
        review_service_enhanced.review_comments.clear()
        review_service_enhanced.assignment_history.clear()

    def test_create_review_with_auto_assign(self):
        """测试创建审核记录并自动分配"""
        record = create_review_record(
            transaction_id="TX001",
            priority="high",
            auto_assign=True,
            assign_strategy="least_busy"
        )

        assert record["transaction_id"] == "TX001"
        assert record["priority"] == "high"
        assert record["status"] == ReviewStatus.PENDING
        assert record["assigned_to"] is not None
        assert record["auto_assigned"] is True
        assert "timeout_at" in record

    def test_create_review_manual_assign(self):
        """测试手动分配审核人"""
        record = create_review_record(
            transaction_id="TX002",
            priority="normal",
            assigned_to="reviewer01",
            auto_assign=False
        )

        assert record["assigned_to"] == "reviewer01"
        assert record["auto_assigned"] is False

    def test_auto_assign_strategies(self):
        """测试不同的自动分配策略"""
        strategies = ["least_busy", "round_robin", "random", "skill_based"]

        for strategy in strategies:
            reviewer = auto_assign_reviewer(priority="high", strategy=strategy)
            assert reviewer is not None
            assert isinstance(reviewer, str)

    def test_update_status_valid_transition(self):
        """测试有效的状态流转"""
        # 创建记录
        create_review_record(
            transaction_id="TX003",
            priority="normal",
            assigned_to="reviewer01"
        )

        # pending -> in_review
        record = update_review_status(
            transaction_id="TX003",
            new_status="in_review",
            reviewer="reviewer01"
        )
        assert record["status"] == "in_review"
        assert record["reviewed_by"] == "reviewer01"

        # in_review -> approved
        record = update_review_status(
            transaction_id="TX003",
            new_status="approved",
            reviewer="reviewer01",
            comment="审核通过"
        )
        assert record["status"] == "approved"

    def test_update_status_invalid_transition(self):
        """测试无效的状态流转"""
        create_review_record(
            transaction_id="TX004",
            priority="normal"
        )

        # pending 不能直接到 approved
        with pytest.raises(ValueError, match="不允许的状态流转"):
            update_review_status(
                transaction_id="TX004",
                new_status="approved",
                reviewer="reviewer01"
            )

    def test_list_pending_reviews_with_timeout(self):
        """测试获取待审核列表（含超时检测）"""
        # 创建一个即将超时的记录
        record = create_review_record(
            transaction_id="TX005",
            priority="urgent",
            assigned_to="reviewer01"
        )

        # 手动设置为已超时
        from app.services import review_service_enhanced
        record["timeout_at"] = (datetime.now() - timedelta(hours=1)).isoformat()
        review_service_enhanced.review_records["TX005"] = record

        # 获取待审核列表
        reviews = list_pending_reviews(include_timeout=True)

        # 应该自动标记为超时
        timeout_review = next((r for r in reviews if r["transaction_id"] == "TX005"), None)
        assert timeout_review is not None
        assert timeout_review["status"] == ReviewStatus.TIMEOUT
        assert timeout_review["is_timeout"] is True

    def test_list_pending_reviews_filtering(self):
        """测试待审核列表筛选"""
        # 创建多条记录
        create_review_record("TX006", priority="high", assigned_to="reviewer01")
        create_review_record("TX007", priority="low", assigned_to="reviewer02")
        create_review_record("TX008", priority="high", assigned_to="reviewer01")

        # 按审核人筛选
        reviews = list_pending_reviews(assigned_to="reviewer01")
        assert len(reviews) == 2
        assert all(r["assigned_to"] == "reviewer01" for r in reviews)

        # 按优先级筛选
        reviews = list_pending_reviews(priority="high")
        assert len(reviews) == 2
        assert all(r["priority"] == "high" for r in reviews)

    def test_get_review_statistics(self):
        """测试审核统计"""
        # 创建多条不同状态的记录
        create_review_record("TX009", priority="high")
        create_review_record("TX010", priority="normal")

        record = create_review_record("TX011", priority="low")
        update_review_status("TX011", "in_review", "reviewer01")
        update_review_status("TX011", "approved", "reviewer01")

        # 获取统计
        stats = get_review_statistics()

        assert stats["total"] == 3
        assert "status_distribution" in stats
        assert "priority_distribution" in stats
        assert "avg_review_time_hours" in stats
        assert "timeout_count" in stats
        assert "auto_assign_rate" in stats

    def test_get_reviewer_workload(self):
        """测试审核人工作量统计"""
        # 创建多条记录
        create_review_record("TX012", priority="urgent", assigned_to="reviewer01")
        create_review_record("TX013", priority="high", assigned_to="reviewer01")
        create_review_record("TX014", priority="normal", assigned_to="reviewer02")

        # 获取工作量
        workload = get_reviewer_workload()

        assert len(workload) >= 2
        assert all("reviewer_id" in w for w in workload)
        assert all("total_load" in w for w in workload)
        assert all("urgent" in w for w in workload)

        # reviewer01 应该有2个任务
        reviewer01_load = next((w for w in workload if w["reviewer_id"] == "reviewer01"), None)
        assert reviewer01_load is not None
        assert reviewer01_load["total_load"] == 2

    def test_priority_timeout_mapping(self):
        """测试不同优先级的超时时间"""
        priorities = {
            "urgent": 2,
            "high": 6,
            "normal": 24,
            "low": 48
        }

        for priority, expected_hours in priorities.items():
            record = create_review_record(
                transaction_id=f"TX_TIMEOUT_{priority}",
                priority=priority
            )

            created_at = datetime.fromisoformat(record["created_at"])
            timeout_at = datetime.fromisoformat(record["timeout_at"])
            actual_hours = (timeout_at - created_at).total_seconds() / 3600

            assert abs(actual_hours - expected_hours) < 0.1  # 允许小误差

    def test_concurrent_assignments(self):
        """测试并发分配（模拟）"""
        # 创建多个记录测试分配
        records = []
        for i in range(10):
            record = create_review_record(
                transaction_id=f"TX_CONCURRENT_{i}",
                priority="normal",
                auto_assign=True,
                assign_strategy="least_busy"
            )
            records.append(record)

        # 验证所有记录都被分配
        assert all(r["assigned_to"] is not None for r in records)

        # 验证分配相对均匀（最少忙策略）
        from collections import Counter
        assignments = Counter(r["assigned_to"] for r in records)
        # 不应该所有任务都分配给同一个人
        assert len(assignments) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
