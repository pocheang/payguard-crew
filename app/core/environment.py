"""
环境配置枚举

提供类型安全的环境配置
"""
import os
from enum import Enum
from typing import Optional


class Environment(str, Enum):
    """环境类型枚举"""
    DEVELOPMENT = "dev"
    DEVELOPMENT_FULL = "development"
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "prod"
    PRODUCTION_FULL = "production"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self in (Environment.PRODUCTION, Environment.PRODUCTION_FULL)

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self in (Environment.DEVELOPMENT, Environment.DEVELOPMENT_FULL, Environment.LOCAL)

    @classmethod
    def from_string(cls, value: str) -> "Environment":
        """从字符串创建枚举，提供友好错误"""
        value_lower = value.lower().strip()
        for env in cls:
            if env.value == value_lower:
                return env

        # 提供友好的错误消息
        valid_values = ", ".join([e.value for e in cls])
        raise ValueError(
            f"Invalid environment: '{value}'. "
            f"Valid values are: {valid_values}"
        )


def get_env(key: str, default: Optional[str] = None) -> str:
    """
    获取环境变量

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        环境变量值或默认值
    """
    return os.getenv(key, default)
