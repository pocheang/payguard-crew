"""
测试审核工作流增强功能
"""
import pytest
from app.services.review_service import (
    auto_assign_reviewer,
    create_review_record,
    get_overdue_reviews,
    check_and_escalate_overdue,
    get_review_history,
    validate_status_transition,
    get_review_statistics,
    ReviewStatus
)


def test_auto_assign_reviewer():
    """测试自动分配审核员"""
    # 测试普通优先级分配
    reviewer = auto_assign_reviewer("normal")
    assert reviewer is not None

    # 测试紧急优先级分配
    urgent_reviewer = auto_assign_reviewer("urgent")
    assert urgent_reviewer is not None


def test_create_review_with_auto_assign():
    """测试创建审核记录时自动分配"""
    transaction_id = "test_tx_auto_assign_001"

    # 启用自动分配
    record = create_review_record(
        transaction_id=transaction_id,
        priority="high",
        assigned_to=None,
        auto_assign=True
    )

    assert record is not None
    assert record['transaction_id'] == transaction_id
    assert record['assigned_to'] is not None  # 应该被自动分配
    assert record['priority'] == "high"


def test_validate_status_transition():
    """测试状态流转验证"""
    # 合法流转
    is_valid, msg = validate_status_transition("pending", "in_review")
    assert is_valid is True

    # 非法流转
    is_valid, msg = validate_status_transition("pending", "approved")
    assert is_valid is False
    assert "不允许" in msg

    # 相同状态
    is_valid, msg = validate_status_transition("pending", "pending")
    assert is_valid is False
    assert "未变更" in msg


def test_get_review_statistics_enhanced():
    """测试增强的统计功能"""
    stats = get_review_statistics()

    # 验证返回的字段
    assert "status_distribution" in stats
    assert "top_reviewers" in stats
    assert "average_review_time_hours" in stats
    assert "priority_distribution" in stats
    assert "overdue_reviews" in stats
    assert "today" in stats

    # 验证审核员统计包含详细信息
    if stats["top_reviewers"]:
        reviewer = stats["top_reviewers"][0]
        assert "reviewer" in reviewer
        assert "total_reviews" in reviewer
        assert "approved" in reviewer
        assert "rejected" in reviewer
        assert "approval_rate" in reviewer
        assert "avg_review_time_hours" in reviewer


def test_get_review_history():
    """测试获取审核历史"""
    # 先创建一个审核记录
    transaction_id = "test_tx_history_001"
    create_review_record(transaction_id, priority="normal")

    # 获取历史
    history = get_review_history(transaction_id)

    assert history is not None
    assert "record" in history
    assert "history" in history
    assert "total_actions" in history
    assert history['record']['transaction_id'] == transaction_id


def test_overdue_detection():
    """测试超时检测"""
    # 获取超时列表（设置为0小时以捕获所有待审核）
    overdue = get_overdue_reviews(timeout_hours=0)

    assert isinstance(overdue, list)
    # 每条记录应该包含 hours_pending 字段
    for record in overdue:
        assert "hours_pending" in record


def test_status_transitions_rules():
    """测试所有状态流转规则"""
    from app.services.review_service import STATUS_TRANSITIONS

    # 验证每个状态都有定义的流转规则
    for status in ReviewStatus:
        assert status in STATUS_TRANSITIONS

    # 验证 ARCHIVED 状态不能流转
    assert STATUS_TRANSITIONS[ReviewStatus.ARCHIVED] == []

    # 验证 PENDING 可以流转到 IN_REVIEW
    assert ReviewStatus.IN_REVIEW in STATUS_TRANSITIONS[ReviewStatus.PENDING]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
