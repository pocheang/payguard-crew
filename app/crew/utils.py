"""
审计工作流辅助工具
"""
import json
from datetime import datetime, timezone
from typing import Any

from app.schemas.audit import AuditLogEntry


JSONDict = dict[str, Any]


def now_iso() -> str:
    """获取当前 ISO 格式时间"""
    return datetime.now(timezone.utc).isoformat()


def json_text(payload: object | None) -> str | None:
    """将对象转换为 JSON 字符串"""
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, default=str)


def append_log(
    logs: list[AuditLogEntry],
    agent_name: str,
    input_data: object | None,
    output_data: object | None,
    status: str,
    latency_ms: int,
    error_message: str | None = None,
) -> None:
    """添加审计日志条目"""
    logs.append(
        AuditLogEntry(
            agent_name=agent_name,
            input_data=json_text(input_data),
            output_data=json_text(output_data),
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
            created_at=now_iso(),
        )
    )


def extract_json_object(raw_output: object) -> JSONDict | None:
    """从原始输出中提取 JSON 对象"""
    text = str(raw_output).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def log_status(error_message: str | None, attempted_crewai: bool) -> str:
    """确定日志状态"""
    if attempted_crewai and error_message:
        return "fallback"
    return "completed"
