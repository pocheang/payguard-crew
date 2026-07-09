"""
审计日志仓储

负责：audit_logs 表的增删改查
"""
import json

from app.db.database import get_connection, init_db
from app.schemas.audit import AuditLogEntry, AuditLogResponse


def _json_text(value: object | None) -> str | None:
    """转换为JSON文本"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def save_audit_log(transaction_id: str, log: AuditLogEntry) -> None:
    """
    保存单条审计日志

    Args:
        transaction_id: 交易ID
        log: 日志条目
    """
    init_db()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_logs (
                transaction_id, agent_name, input_data, output_data,
                status, latency_ms, error_message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                log.agent_name,
                _json_text(log.input_data),
                _json_text(log.output_data),
                log.status,
                log.latency_ms,
                log.error_message,
                log.created_at,
            ),
        )


def save_audit_logs_batch(transaction_id: str, logs: list[AuditLogEntry]) -> None:
    """
    批量保存审计日志

    优化：使用executemany批量插入
    """
    if not logs:
        return

    init_db()
    with get_connection() as connection:
        # 先删除旧日志
        connection.execute(
            "DELETE FROM audit_logs WHERE transaction_id = ?",
            (transaction_id,)
        )

        # 批量插入
        log_data = [
            (
                transaction_id,
                log.agent_name,
                _json_text(log.input_data),
                _json_text(log.output_data),
                log.status,
                log.latency_ms,
                log.error_message,
                log.created_at,
            )
            for log in logs
        ]

        connection.executemany(
            """
            INSERT INTO audit_logs (
                transaction_id, agent_name, input_data, output_data,
                status, latency_ms, error_message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            log_data,
        )


def get_audit_logs(transaction_id: str) -> AuditLogResponse:
    """
    获取审计日志

    Args:
        transaction_id: 交易ID

    Returns:
        审计日志响应
    """
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT agent_name, input_data, output_data,
                   status, latency_ms, error_message, created_at
            FROM audit_logs
            WHERE transaction_id = ?
            ORDER BY created_at ASC
            """,
            (transaction_id,),
        ).fetchall()

    return AuditLogResponse(
        transaction_id=transaction_id,
        logs=[
            AuditLogEntry(
                agent_name=row["agent_name"],
                input_data=row["input_data"],
                output_data=row["output_data"],
                status=row["status"],
                latency_ms=row["latency_ms"],
                error_message=row["error_message"],
                created_at=row["created_at"],
            )
            for row in rows
        ],
    )
