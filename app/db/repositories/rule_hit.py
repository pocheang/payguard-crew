"""
规则命中仓储

负责：rule_hits 表的增删改查
"""
from app.db.database import get_connection, init_db


def save_rule_hits(transaction_id: str, rules: list[dict]) -> None:
    """
    保存规则命中记录

    优化：使用executemany批量插入

    Args:
        transaction_id: 交易ID
        rules: 规则列表
    """
    if not rules:
        return

    init_db()
    with get_connection() as connection:
        # 先删除旧记录
        connection.execute(
            "DELETE FROM rule_hits WHERE transaction_id = ?",
            (transaction_id,)
        )

        # 批量插入
        rule_data = [
            (
                transaction_id,
                rule["rule_id"],
                rule["rule_name"],
                rule["reason"],
                rule["score"],
            )
            for rule in rules
        ]

        connection.executemany(
            """
            INSERT INTO rule_hits (
                transaction_id, rule_id, rule_name, reason, score
            ) VALUES (?, ?, ?, ?, ?)
            """,
            rule_data,
        )


def get_rule_hits(transaction_id: str) -> list[dict]:
    """
    获取规则命中记录

    Args:
        transaction_id: 交易ID

    Returns:
        规则列表
    """
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT rule_id, rule_name, reason, score
            FROM rule_hits
            WHERE transaction_id = ?
            ORDER BY id ASC
            """,
            (transaction_id,),
        ).fetchall()

    return [
        {
            "rule_id": row["rule_id"],
            "rule_name": row["rule_name"],
            "reason": row["reason"],
            "score": row["score"],
        }
        for row in rows
    ]
