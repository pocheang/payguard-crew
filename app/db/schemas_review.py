"""
审核工作流数据库Schema

新增表：
1. review_records - 审核记录
2. review_comments - 审核评论
"""

# 审核记录表
REVIEW_RECORDS_SCHEMA = """
CREATE TABLE IF NOT EXISTS review_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    assigned_to TEXT,
    reviewer TEXT,
    priority TEXT DEFAULT 'normal',
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES audit_reports(transaction_id)
)
"""

# 审核评论表
REVIEW_COMMENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS review_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    comment TEXT NOT NULL,
    action TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES audit_reports(transaction_id)
)
"""

# 索引
REVIEW_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_review_records_status ON review_records(status)",
    "CREATE INDEX IF NOT EXISTS idx_review_records_assigned_to ON review_records(assigned_to)",
    "CREATE INDEX IF NOT EXISTS idx_review_records_transaction_id ON review_records(transaction_id)",
    "CREATE INDEX IF NOT EXISTS idx_review_comments_transaction_id ON review_comments(transaction_id)",
]


def init_review_tables():
    """初始化审核工作流表"""
    from app.db.database import get_connection

    with get_connection() as conn:
        # 创建表
        conn.execute(REVIEW_RECORDS_SCHEMA)
        conn.execute(REVIEW_COMMENTS_SCHEMA)

        # 创建索引
        for index_sql in REVIEW_INDEXES:
            conn.execute(index_sql)

        conn.commit()

    print("✅ Review workflow tables initialized")
