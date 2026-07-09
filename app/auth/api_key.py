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

    所有环境都必须配置 API_KEYS

    Raises:
        HTTPException: 401 如果未提供或API Key无效
        HTTPException: 503 如果未配置API Keys
    """
    valid_keys = get_valid_api_keys()

    # 如果未配置 API Keys，拒绝访问
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service misconfigured: API authentication not enabled. "
                   "Administrator must configure API_KEYS environment variable.",
        )

    # 检查是否提供了 API Key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Add X-API-Key header to your request.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # 验证 API Key
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return api_key
