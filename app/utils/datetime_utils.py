"""日期时间工具函数"""
from datetime import datetime, timezone


def now_iso() -> str:
    """返回当前UTC时间的ISO格式字符串"""
    return datetime.now(timezone.utc).isoformat()
