"""数据库工具函数"""
from typing import Any


ALLOWED_TABLES = {
    'audit_logs',
    'rule_hits',
    'audit_reports'
}


def rows_to_dicts(rows: list) -> list[dict]:
    """将数据库行对象转换为字典列表"""
    return [dict(row) for row in rows]


def cleanup_transaction_data(connection: Any, table_name: str, transaction_id: str) -> None:
    """
    通用函数：删除指定交易的旧数据

    Args:
        connection: 数据库连接
        table_name: 表名
        transaction_id: 交易ID

    Raises:
        ValueError: 如果表名不在允许列表中
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}. Allowed: {ALLOWED_TABLES}")

    connection.execute(
        f"DELETE FROM {table_name} WHERE transaction_id = ?",
        (transaction_id,)
    )
