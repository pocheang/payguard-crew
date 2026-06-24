"""API Key 认证模块"""
import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_valid_api_keys() -> set[str]:
    """获取有效的 API Keys"""
    keys = os.getenv("API_KEYS", "")
    if not keys:
        return set()
    return set(k.strip() for k in keys.split(",") if k.strip())


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """验证 API Key

    如果未配置 API_KEYS 环境变量，将允许所有请求（开发模式）
    生产环境必须配置 API_KEYS
    """
    valid_keys = get_valid_api_keys()

    # 如果未配置 API Keys，允许访问（开发模式）
    if not valid_keys:
        import warnings
        warnings.warn(
            "⚠️ 未配置 API_KEYS 环境变量，API 未受保护！\n"
            "生产环境请务必配置 API_KEYS",
            UserWarning,
            stacklevel=2
        )
        return "dev-mode"

    # 检查是否提供了 API Key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 API Key。请在请求头中添加 X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # 验证 API Key
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return api_key
