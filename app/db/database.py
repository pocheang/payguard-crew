"""
数据库连接模块

提供数据库连接和初始化功能
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import get_settings

# 🔒 安全：允许的表名白名单（防止 SQL 注入）
ALLOWED_TABLES = {"audit_reports", "audit_logs", "rule_hits"}


def get_database_path() -> Path:
    """获取数据库路径"""
    return get_settings().db_path


def _ensure_parent_dir(db_path: Path) -> None:
    """确保数据库目录存在"""
    db_path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """获取数据库连接（带自动提交和回滚）"""
    db_path = get_database_path()
    _ensure_parent_dir(db_path)
    connection = sqlite3.connect(db_path, timeout=30.0)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI 依赖注入使用的数据库连接"""
    with get_connection() as conn:
        yield conn


def init_db() -> None:
    """初始化数据库"""
    from app.db.schemas import (
        AUDIT_REPORTS_SCHEMA,
        AUDIT_LOGS_SCHEMA,
        RULE_HITS_SCHEMA
    )
    from app.db.migrations import (
        rebuild_audit_reports,
        rebuild_audit_logs,
        rebuild_rule_hits
    )

    with get_connection() as connection:
        # 创建表
        connection.execute(AUDIT_REPORTS_SCHEMA)
        connection.execute(AUDIT_LOGS_SCHEMA)
        connection.execute(RULE_HITS_SCHEMA)
        connection.commit()

        # 验证表结构
        connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_reports'"
        )
        connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'"
        )
        connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='rule_hits'"
        )

        # 重建表结构（如果列不匹配）
        rebuild_audit_reports(connection)
        rebuild_audit_logs(connection)
        rebuild_rule_hits(connection)
