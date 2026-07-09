"""API响应标准化工具"""
from typing import Any, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """标准成功响应"""
    success: bool = True
    data: T


def success_response(data: Any) -> dict:
    """
    创建标准成功响应

    Args:
        data: 响应数据

    Returns:
        标准格式的成功响应字典
    """
    return {"success": True, "data": data}
