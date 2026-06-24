"""
数据库迁移工具
"""
import sqlite3
from app.db.schemas import (
    AUDIT_REPORT_COLUMNS,
    AUDIT_LOG_COLUMNS,
    RULE_HIT_COLUMNS,
    AUDIT_REPORTS_SCHEMA,
    AUDIT_LOGS_SCHEMA,
    RULE_HITS_SCHEMA
)

# 🔒 安全：允许的表名白名单（防止 SQL 注入）
ALLOWED_TABLES = {"audit_reports", "audit_logs", "rule_hits"}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> list[str]:
    """获取表的列名（带安全验证）"""
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row["name"] for row in rows]


def _create_replacement_table(
    connection: sqlite3.Connection, schema: str, old_name: str, new_name: str
) -> None:
    """创建替换表（带安全验证）"""
    if old_name not in ALLOWED_TABLES or new_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table names: {old_name}, {new_name}")

    connection.execute(f"DROP TABLE IF EXISTS {new_name}")
    connection.execute(schema.replace(old_name, new_name, 1))


def rebuild_audit_reports(connection: sqlite3.Connection) -> None:
    """重建 audit_reports 表结构"""
    table_name = "audit_reports"

    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    old_columns = _table_columns(connection, table_name)
    expected_columns = AUDIT_REPORT_COLUMNS

    if old_columns == expected_columns:
        return

    old_name = table_name
    new_name = f"{table_name}_new"
    _create_replacement_table(connection, AUDIT_REPORTS_SCHEMA, old_name, new_name)

    rows = [dict(row) for row in connection.execute("SELECT * FROM audit_reports").fetchall()]

    for row in rows:
        connection.execute(
            f"""
            INSERT INTO {new_name} (
                transaction_id, user_id, merchant_id, risk_score, risk_level,
                decision, summary, suggestion, requires_manual_review, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("transaction_id"),
                row.get("user_id"),
                row.get("merchant_id"),
                row.get("risk_score"),
                row.get("risk_level"),
                row.get("decision"),
                row.get("summary"),
                row.get("suggestion"),
                row.get("requires_manual_review"),
                row.get("created_at"),
            ),
        )

    connection.execute("DROP TABLE audit_reports")
    connection.execute("ALTER TABLE audit_reports_new RENAME TO audit_reports")


def rebuild_audit_logs(connection: sqlite3.Connection) -> None:
    """重建 audit_logs 表结构"""
    table_name = "audit_logs"

    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    old_columns = _table_columns(connection, table_name)
    expected_columns = AUDIT_LOG_COLUMNS

    if old_columns == expected_columns:
        return

    old_name = table_name
    new_name = f"{table_name}_new"
    _create_replacement_table(connection, AUDIT_LOGS_SCHEMA, old_name, new_name)

    rows = [dict(row) for row in connection.execute("SELECT * FROM audit_logs").fetchall()]

    for row in rows:
        connection.execute(
            f"""
            INSERT INTO {new_name} (
                transaction_id, agent_name, input_data, output_data,
                status, error_message, latency_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("transaction_id"),
                row.get("agent_name"),
                row.get("input_data"),
                row.get("output_data"),
                row.get("status"),
                row.get("error_message"),
                row.get("latency_ms"),
                row.get("created_at"),
            ),
        )

    connection.execute("DROP TABLE audit_logs")
    connection.execute("ALTER TABLE audit_logs_new RENAME TO audit_logs")


def rebuild_rule_hits(connection: sqlite3.Connection) -> None:
    """重建 rule_hits 表结构"""
    table_name = "rule_hits"

    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    old_columns = _table_columns(connection, table_name)
    expected_columns = RULE_HIT_COLUMNS

    if old_columns == expected_columns:
        return

    old_name = table_name
    new_name = f"{table_name}_new"
    _create_replacement_table(connection, RULE_HITS_SCHEMA, old_name, new_name)

    rows = [dict(row) for row in connection.execute("SELECT * FROM rule_hits").fetchall()]

    for row in rows:
        connection.execute(
            f"""
            INSERT INTO {new_name} (
                transaction_id, rule_id, rule_name, reason, score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("transaction_id"),
                row.get("rule_id"),
                row.get("rule_name"),
                row.get("reason"),
                row.get("score"),
                row.get("created_at"),
            ),
        )

    connection.execute("DROP TABLE rule_hits")
    connection.execute("ALTER TABLE rule_hits_new RENAME TO rule_hits")
