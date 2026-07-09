"""
审核工作流服务

功能：
1. 状态流转管理
2. 分配审核人
3. 添加评论
4. 审核历史
"""
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum

from app.db.database import get_connection


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "pending"           # 待审核
    IN_REVIEW = "in_review"       # 审核中
    APPROVED = "approved"         # 已批准
    REJECTED = "rejected"         # 已拒绝
    ESCALATED = "escalated"       # 已升级
    ARCHIVED = "archived"         # 已归档


class ReviewPriority(str, Enum):
    """优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# 状态流转规则
STATUS_TRANSITIONS = {
    ReviewStatus.PENDING: [ReviewStatus.IN_REVIEW, ReviewStatus.ARCHIVED],
    ReviewStatus.IN_REVIEW: [ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.ESCALATED],
    ReviewStatus.APPROVED: [ReviewStatus.ARCHIVED],
    ReviewStatus.REJECTED: [ReviewStatus.ARCHIVED, ReviewStatus.IN_REVIEW],
    ReviewStatus.ESCALATED: [ReviewStatus.IN_REVIEW, ReviewStatus.ARCHIVED],
    ReviewStatus.ARCHIVED: [],  # 归档后不可流转
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_review_record(
    transaction_id: str,
    priority: str = "normal",
    assigned_to: Optional[str] = None
) -> dict:
    """
    创建审核记录

    Args:
        transaction_id: 交易ID
        priority: 优先级 (low/normal/high/urgent)
        assigned_to: 分配给谁

    Returns:
        创建的审核记录
    """
    now = _now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO review_records (
                transaction_id, status, priority, assigned_to, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (transaction_id, ReviewStatus.PENDING, priority, assigned_to, now, now)
        )
        conn.commit()

    return get_review_record(transaction_id)


def get_review_record(transaction_id: str) -> Optional[dict]:
    """获取审核记录"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM review_records WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()

    return dict(row) if row else None


def update_review_status(
    transaction_id: str,
    new_status: str,
    reviewer: str,
    comment: Optional[str] = None
) -> dict:
    """
    更新审核状态

    Args:
        transaction_id: 交易ID
        new_status: 新状态
        reviewer: 审核人
        comment: 备注

    Returns:
        更新后的审核记录

    Raises:
        ValueError: 状态流转不合法
    """
    # 获取当前记录
    record = get_review_record(transaction_id)
    if not record:
        raise ValueError(f"审核记录不存在: {transaction_id}")

    current_status = ReviewStatus(record['status'])
    new_status_enum = ReviewStatus(new_status)

    # 验证状态流转
    if new_status_enum not in STATUS_TRANSITIONS[current_status]:
        raise ValueError(
            f"不允许的状态流转: {current_status} -> {new_status_enum}. "
            f"允许的状态: {STATUS_TRANSITIONS[current_status]}"
        )

    now = _now_iso()

    with get_connection() as conn:
        # 更新状态
        conn.execute(
            """
            UPDATE review_records
            SET status = ?, reviewer = ?, reviewed_at = ?, updated_at = ?
            WHERE transaction_id = ?
            """,
            (new_status, reviewer, now, now, transaction_id)
        )

        # 添加评论
        if comment:
            conn.execute(
                """
                INSERT INTO review_comments (
                    transaction_id, user_id, comment, action, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (transaction_id, reviewer, comment, new_status, now)
            )

        conn.commit()

    return get_review_record(transaction_id)


def assign_reviewer(
    transaction_id: str,
    assigned_to: str,
    assigner: str
) -> dict:
    """
    分配审核人

    Args:
        transaction_id: 交易ID
        assigned_to: 分配给谁
        assigner: 分配人

    Returns:
        更新后的审核记录
    """
    now = _now_iso()

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE review_records
            SET assigned_to = ?, updated_at = ?
            WHERE transaction_id = ?
            """,
            (assigned_to, now, transaction_id)
        )

        # 记录分配动作
        conn.execute(
            """
            INSERT INTO review_comments (
                transaction_id, user_id, comment, action, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (transaction_id, assigner, f"分配给: {assigned_to}", "assigned", now)
        )

        conn.commit()

    return get_review_record(transaction_id)


def add_comment(
    transaction_id: str,
    user_id: str,
    comment: str
) -> dict:
    """
    添加评论

    Args:
        transaction_id: 交易ID
        user_id: 用户ID
        comment: 评论内容

    Returns:
        添加的评论
    """
    now = _now_iso()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO review_comments (
                transaction_id, user_id, comment, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (transaction_id, user_id, comment, now)
        )
        comment_id = cursor.lastrowid
        conn.commit()

        row = conn.execute(
            "SELECT * FROM review_comments WHERE id = ?",
            (comment_id,)
        ).fetchone()

    return dict(row)


def get_comments(transaction_id: str) -> List[dict]:
    """获取所有评论"""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM review_comments
            WHERE transaction_id = ?
            ORDER BY created_at ASC
            """,
            (transaction_id,)
        ).fetchall()

    return [dict(row) for row in rows]


def list_pending_reviews(
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100
) -> List[dict]:
    """
    查询待审核列表

    Args:
        assigned_to: 筛选分配人
        priority: 筛选优先级
        limit: 返回数量

    Returns:
        审核记录列表
    """
    query = """
        SELECT r.*, a.risk_score, a.risk_level, a.user_id, a.merchant_id
        FROM review_records r
        JOIN audit_reports a ON r.transaction_id = a.transaction_id
        WHERE r.status IN ('pending', 'in_review')
    """
    params = []

    if assigned_to:
        query += " AND r.assigned_to = ?"
        params.append(assigned_to)

    if priority:
        query += " AND r.priority = ?"
        params.append(priority)

    query += " ORDER BY r.priority DESC, r.created_at ASC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_review_statistics() -> dict:
    """获取审核统计"""
    with get_connection() as conn:
        # 按状态统计
        status_stats = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM review_records
            GROUP BY status
            """
        ).fetchall()

        # 按审核人统计
        reviewer_stats = conn.execute(
            """
            SELECT reviewer, COUNT(*) as count
            FROM review_records
            WHERE reviewer IS NOT NULL
            GROUP BY reviewer
            ORDER BY count DESC
            LIMIT 10
            """
        ).fetchall()

        # 平均审核时间
        avg_time = conn.execute(
            """
            SELECT AVG(
                (julianday(reviewed_at) - julianday(created_at)) * 24
            ) as avg_hours
            FROM review_records
            WHERE reviewed_at IS NOT NULL
            """
        ).fetchone()

    return {
        "status_distribution": {
            row['status']: row['count'] for row in status_stats
        },
        "top_reviewers": [
            {"reviewer": row['reviewer'], "count": row['count']}
            for row in reviewer_stats
        ],
        "average_review_time_hours": round(avg_time['avg_hours'] or 0, 2)
    }
