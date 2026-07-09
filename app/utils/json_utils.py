"""JSON序列化工具函数"""
import json
from typing import Any


def json_text(value: Any | None) -> str | None:
    """
    将值转换为JSON文本表示（用于数据库存储）

    Args:
        value: 要序列化的值

    Returns:
        JSON字符串，如果value为None则返回None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)
