"""
审计报告仓储

负责：audit_reports 表的增删改查
"""
from app.db.database import get_connection, init_db
from app.schemas.audit import AuditReportRecord, AuditResponse
from app.schemas.transaction import TransactionInput
from app.utils.datetime_utils import now_iso


def save_audit_report(tx: TransactionInput, report: AuditResponse) -> None:
    """
    保存审计报告

    Args:
        tx: 交易输入
        report: 审计响应
    """
    created_at = now_iso()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_reports (
                transaction_id, user_id, merchant_id,
                risk_score, risk_level, decision,
                summary, suggestion, requires_manual_review,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(transaction_id) DO UPDATE SET
                user_id = excluded.user_id,
                merchant_id = excluded.merchant_id,
                risk_score = excluded.risk_score,
                risk_level = excluded.risk_level,
                decision = excluded.decision,
                summary = excluded.summary,
                suggestion = excluded.suggestion,
                requires_manual_review = excluded.requires_manual_review,
                created_at = excluded.created_at
            """,
            (
                report.transaction_id,
                tx.user_id,
                tx.merchant_id,
                report.risk_score,
                report.risk_level,
                report.decision,
                report.summary,
                report.suggestion,
                int(report.requires_manual_review),
                created_at,
            ),
        )


def get_audit_report(transaction_id: str) -> AuditReportRecord | None:
    """
    获取审计报告

    优化：在单次连接中查询所有数据
    """
    with get_connection() as connection:
        report_row = connection.execute(
            """
            SELECT transaction_id, user_id, merchant_id,
                   risk_score, risk_level, decision,
                   summary, suggestion, requires_manual_review,
                   created_at
            FROM audit_reports
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if report_row is None:
            return None

        # 在同一连接中查询规则
        rule_rows = connection.execute(
            """
            SELECT rule_id, rule_name, reason, score
            FROM rule_hits
            WHERE transaction_id = ?
            ORDER BY id ASC
            """,
            (transaction_id,),
        ).fetchall()

    from app.schemas.audit import TriggeredRule

    return AuditReportRecord(
        transaction_id=report_row["transaction_id"],
        user_id=report_row["user_id"],
        merchant_id=report_row["merchant_id"],
        risk_score=report_row["risk_score"],
        risk_level=report_row["risk_level"],
        decision=report_row["decision"],
        summary=report_row["summary"],
        suggestion=report_row["suggestion"],
        requires_manual_review=bool(report_row["requires_manual_review"]),
        created_at=report_row["created_at"],
        triggered_rules=[
            TriggeredRule(
                rule_id=row["rule_id"],
                rule_name=row["rule_name"],
                reason=row["reason"],
                score=row["score"],
            )
            for row in rule_rows
        ],
    )
