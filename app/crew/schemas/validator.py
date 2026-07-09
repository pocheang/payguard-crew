"""
JSON Schema验证器（简化版）

将验证逻辑从schema_validator.py中提取出来，保持单一职责
"""
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_agent_output(agent_name: str, payload: dict[str, Any], schema: dict) -> tuple[bool, Optional[str]]:
    """
    验证Agent输出是否符合Schema

    Args:
        agent_name: Agent名称
        payload: Agent返回的JSON数据
        schema: JSON Schema定义

    Returns:
        (is_valid, error_message)
    """
    try:
        errors = _validate_schema(payload, schema, path="root")
        if errors:
            error_msg = "; ".join(errors[:3])  # 只显示前3个错误
            logger.error(f"Agent {agent_name} output validation failed: {error_msg}")
            return False, error_msg

        return True, None

    except Exception as e:
        logger.error(f"Schema validation exception for {agent_name}: {e}")
        return False, str(e)


def _validate_schema(data: Any, schema: dict, path: str = "root") -> list[str]:
    """递归验证JSON Schema（简化实现）"""
    errors = []
    expected_type = schema.get("type")

    if expected_type and not _check_type(data, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(data).__name__}")
        return errors

    # 验证required字段
    if expected_type == "object" and "required" in schema and isinstance(data, dict):
        for field in schema["required"]:
            if field not in data:
                errors.append(f"{path}: missing '{field}'")

    # 验证properties
    if expected_type == "object" and "properties" in schema and isinstance(data, dict):
        for field, field_schema in schema["properties"].items():
            if field in data:
                errors.extend(_validate_schema(data[field], field_schema, f"{path}.{field}"))

    # 验证array
    if expected_type == "array" and isinstance(data, list):
        if "items" in schema:
            for i, item in enumerate(data):
                errors.extend(_validate_schema(item, schema["items"], f"{path}[{i}]"))

        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: array too short")
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{path}: array too long")

    # 验证string长度
    if expected_type == "string" and isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: string too short")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(f"{path}: string too long")

    # 验证integer范围
    if expected_type == "integer" and isinstance(data, int):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: value {data} < {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: value {data} > {schema['maximum']}")

    # 验证enum
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: '{data}' not in {schema['enum']}")

    return errors


def _check_type(data: Any, expected_type: str) -> bool:
    """检查数据类型"""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    expected_python_type = type_map.get(expected_type)
    return expected_python_type and isinstance(data, expected_python_type)
