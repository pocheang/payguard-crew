"""
数据库表结构定义
"""

# 列定义
AUDIT_REPORT_COLUMNS = [
    "id",
    "transaction_id",
    "user_id",
    "merchant_id",
    "risk_score",
    "risk_level",
    "decision",
    "summary",
    "suggestion",
    "requires_manual_review",
    "created_at",
]

AUDIT_LOG_COLUMNS = [
    "id",
    "transaction_id",
    "agent_name",
    "input_data",
    "output_data",
    "status",
    "error_message",
    "latency_ms",
    "created_at",
]

RULE_HIT_COLUMNS = [
    "id",
    "transaction_id",
    "rule_id",
    "rule_name",
    "reason",
    "score",
    "created_at",
]

# 表结构定义
AUDIT_REPORTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    user_id TEXT,
    merchant_id TEXT,
    risk_score INTEGER,
    risk_level TEXT,
    decision TEXT,
    summary TEXT,
    suggestion TEXT,
    requires_manual_review BOOLEAN,
    created_at TEXT
)
"""

AUDIT_LOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    agent_name TEXT,
    input_data TEXT,
    output_data TEXT,
    status TEXT,
    error_message TEXT,
    latency_ms INTEGER,
    created_at TEXT
)
"""

RULE_HITS_SCHEMA = """
CREATE TABLE IF NOT EXISTS rule_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    rule_id TEXT,
    rule_name TEXT,
    reason TEXT,
    score INTEGER,
    created_at TEXT
)
"""
