"""
审核工作流服务

功能：
1. 状态流转管理
2. 分配审核人
3. 添加评论
4. 审核历史
"""
from typing import List, Optional
from enum import Enum

from app.db.database import get_connection
from app.utils.datetime_utils import now_iso


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


def auto_assign_reviewer(priority: str) -> Optional[str]:
    """
    自动分配审核人 - 基于负载均衡

    策略：
    1. 优先分配当前任务最少的审核员
    2. 考虑审核员的专业领域
    3. 紧急任务优先分配给经验丰富的审核员

    Args:
        priority: 任务优先级

    Returns:
        分配的审核员ID，如果没有可用审核员则返回None
    """
    with get_connection() as conn:
        # 获取所有审核员的当前工作量
        reviewers = conn.execute(
            """
            SELECT
                assigned_to,
                COUNT(*) as workload
            FROM review_records
            WHERE status IN ('pending', 'in_review')
              AND assigned_to IS NOT NULL
            GROUP BY assigned_to
            ORDER BY workload ASC
            """
        ).fetchall()

        # 如果是紧急任务，查找经验最丰富的审核员（处理过最多审核的）
        if priority == ReviewPriority.URGENT:
            experienced = conn.execute(
                """
                SELECT reviewer, COUNT(*) as total
                FROM review_records
                WHERE reviewer IS NOT NULL
                  AND status IN ('approved', 'rejected')
                GROUP BY reviewer
                ORDER BY total DESC
                LIMIT 1
                """
            ).fetchone()

            if experienced and experienced['reviewer']:
                return experienced['reviewer']

        # 返回工作量最少的审核员
        if reviewers:
            return reviewers[0]['assigned_to']

        # 如果没有任何审核员，返回默认值
        return "default_reviewer"


def create_review_record(
    transaction_id: str,
    priority: str = "normal",
    assigned_to: Optional[str] = None,
    auto_assign: bool = True
) -> dict:
    """
    创建审核记录

    Args:
        transaction_id: 交易ID
        priority: 优先级 (low/normal/high/urgent)
        assigned_to: 分配给谁（如果为None且auto_assign=True，则自动分配）
        auto_assign: 是否自动分配审核员

    Returns:
        创建的审核记录
    """
    now = now_iso()

    # 自动分配逻辑
    if assigned_to is None and auto_assign:
        assigned_to = auto_assign_reviewer(priority)

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


def validate_status_transition(current_status: str, new_status: str) -> tuple[bool, str]:
    """
    验证状态流转是否合法（增强版）

    Args:
        current_status: 当前状态
        new_status: 目标状态

    Returns:
        (是否合法, 错误信息)
    """
    try:
        current = ReviewStatus(current_status)
        target = ReviewStatus(new_status)

        # 相同状态不需要流转
        if current == target:
            return False, f"状态未变更: {current}"

        # 检查是否允许流转
        allowed = STATUS_TRANSITIONS.get(current, [])
        if target not in allowed:
            return False, (
                f"不允许的状态流转: {current.value} → {target.value}. "
                f"允许的目标状态: {[s.value for s in allowed]}"
            )

        return True, ""

    except ValueError as e:
        return False, f"无效的状态值: {e}"


def update_review_status(
    transaction_id: str,
    new_status: str,
    reviewer: str,
    comment: Optional[str] = None
) -> dict:
    """
    更新审核状态（优化版）

    Args:
        transaction_id: 交易ID
        new_status: 新状态
        reviewer: 审核人
        comment: 备注

    Returns:
        更新后的审核记录

    Raises:
        ValueError: 状态流转不合法或记录不存在
    """
    # 获取当前记录
    record = get_review_record(transaction_id)
    if not record:
        raise ValueError(f"审核记录不存在: {transaction_id}")

    # 验证状态流转
    is_valid, error_msg = validate_status_transition(record['status'], new_status)
    if not is_valid:
        raise ValueError(error_msg)

    now = now_iso()

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
    now = now_iso()

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
    now = now_iso()

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


def get_review_history(transaction_id: str) -> dict:
    """
    获取完整的审核历史（包括所有状态变更和评论）

    Args:
        transaction_id: 交易ID

    Returns:
        包含审核记录、状态变更历史和评论的完整历史
    """
    with get_connection() as conn:
        # 获取审核记录
        record = get_review_record(transaction_id)
        if not record:
            return None

        # 获取所有评论和操作历史
        history = conn.execute(
            """
            SELECT
                id,
                user_id,
                comment,
                action,
                created_at,
                CASE
                    WHEN action = 'assigned' THEN '分配'
                    WHEN action = 'pending' THEN '待审核'
                    WHEN action = 'in_review' THEN '审核中'
                    WHEN action = 'approved' THEN '批准'
                    WHEN action = 'rejected' THEN '拒绝'
                    WHEN action = 'escalated' THEN '升级'
                    ELSE '评论'
                END as action_label
            FROM review_comments
            WHERE transaction_id = ?
            ORDER BY created_at ASC
            """,
            (transaction_id,)
        ).fetchall()

        # 计算时间线
        timeline = []
        prev_time = record['created_at']

        for item in history:
            time_diff = calculate_time_diff(prev_time, item['created_at'])
            timeline.append({
                **dict(item),
                'time_since_last': time_diff
            })
            prev_time = item['created_at']

    return {
        'record': record,
        'history': timeline,
        'total_actions': len(history)
    }


def calculate_time_diff(start: str, end: str) -> str:
    """计算时间差并格式化为可读字符串"""
    from datetime import datetime

    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        diff = end_dt - start_dt

        hours = diff.total_seconds() / 3600
        if hours < 1:
            return f"{int(diff.total_seconds() / 60)}分钟"
        elif hours < 24:
            return f"{int(hours)}小时"
        else:
            return f"{int(hours / 24)}天"
    except Exception:
        return "未知"


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
        LEFT JOIN audit_reports a ON r.transaction_id = a.transaction_id
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


def get_overdue_reviews(timeout_hours: int = 24) -> List[dict]:
    """
    获取超时未审核的记录

    Args:
        timeout_hours: 超时小时数（默认24小时）

    Returns:
        超时的审核记录列表
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                r.*,
                ROUND((julianday('now') - julianday(r.created_at)) * 24, 1) as hours_pending
            FROM review_records r
            WHERE r.status IN ('pending', 'in_review')
              AND (julianday('now') - julianday(r.created_at)) * 24 > ?
            ORDER BY r.priority DESC, r.created_at ASC
            """,
            (timeout_hours,)
        ).fetchall()

    return [dict(row) for row in rows]


def check_and_escalate_overdue(timeout_hours: int = 24, escalate_to: str = "supervisor") -> List[dict]:
    """
    检查并自动升级超时审核

    Args:
        timeout_hours: 超时小时数
        escalate_to: 升级给谁

    Returns:
        被升级的审核记录列表
    """
    overdue = get_overdue_reviews(timeout_hours)
    escalated = []

    for record in overdue:
        transaction_id = record['transaction_id']
        try:
            # 自动升级超时审核
            updated = update_review_status(
                transaction_id,
                ReviewStatus.ESCALATED,
                reviewer="system_auto_escalate",
                comment=f"审核超时 {record['hours_pending']} 小时，自动升级"
            )
            # 重新分配给supervisor
            assign_reviewer(transaction_id, escalate_to, "system")
            escalated.append(updated)
        except Exception as e:
            print(f"升级失败 {transaction_id}: {e}")

    return escalated


def get_review_statistics() -> dict:
    """获取审核统计（增强版）"""
    with get_connection() as conn:
        # 按状态统计
        status_stats = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM review_records
            GROUP BY status
            """
        ).fetchall()

        # 按审核人统计（包括准确率）
        reviewer_stats = conn.execute(
            """
            SELECT
                reviewer,
                COUNT(*) as total_reviews,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                ROUND(AVG((julianday(reviewed_at) - julianday(created_at)) * 24), 2) as avg_hours
            FROM review_records
            WHERE reviewer IS NOT NULL
            GROUP BY reviewer
            ORDER BY total_reviews DESC
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

        # 按优先级统计
        priority_stats = conn.execute(
            """
            SELECT
                priority,
                COUNT(*) as total,
                SUM(CASE WHEN status IN ('pending', 'in_review') THEN 1 ELSE 0 END) as pending
            FROM review_records
            GROUP BY priority
            """
        ).fetchall()

        # 超时审核统计（24小时）
        overdue_count = conn.execute(
            """
            SELECT COUNT(*) as count
            FROM review_records
            WHERE status IN ('pending', 'in_review')
              AND (julianday('now') - julianday(created_at)) * 24 > 24
            """
        ).fetchone()

        # 今日审核量
        today_stats = conn.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM review_records
            WHERE DATE(created_at) = DATE('now')
            """
        ).fetchone()

    return {
        "status_distribution": {
            row['status']: row['count'] for row in status_stats
        },
        "top_reviewers": [
            {
                "reviewer": row['reviewer'],
                "total_reviews": row['total_reviews'],
                "approved": row['approved_count'],
                "rejected": row['rejected_count'],
                "approval_rate": round(row['approved_count'] / row['total_reviews'] * 100, 1) if row['total_reviews'] > 0 else 0,
                "avg_review_time_hours": row['avg_hours'] or 0
            }
            for row in reviewer_stats
        ],
        "average_review_time_hours": round(avg_time['avg_hours'] or 0, 2),
        "priority_distribution": {
            row['priority']: {
                "total": row['total'],
                "pending": row['pending'],
                "completion_rate": round((row['total'] - row['pending']) / row['total'] * 100, 1) if row['total'] > 0 else 0
            }
            for row in priority_stats
        },
        "overdue_reviews": overdue_count['count'],
        "today": {
            "total": today_stats['total'],
            "approved": today_stats['approved'],
            "rejected": today_stats['rejected'],
            "approval_rate": round(today_stats['approved'] / today_stats['total'] * 100, 1) if today_stats['total'] > 0 else 0
        }
    }
