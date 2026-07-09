"""
速率限制中间件

使用滑动窗口算法限制 API 调用频率，防止滥用
生产环境建议使用Redis存储，开发环境可使用内存存储
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


def rate_limit_key_func(request: Request) -> str:
    """
    生成速率限制的键

    优先使用 API Key，其次使用 IP 地址
    """
    # 优先使用 API Key（如果已认证）
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"

    # 使用 IP 地址
    return f"ip:{get_remote_address(request)}"


# 创建限流器实例
# 生产环境使用Redis: REDIS_URL=redis://localhost:6379/0
# 开发环境使用内存: REDIS_URL未设置
REDIS_URL = os.getenv("REDIS_URL")
storage_uri = REDIS_URL if REDIS_URL else "memory://"

if not REDIS_URL:
    import warnings
    warnings.warn(
        "⚠️ Rate limiting using memory storage. For production, set REDIS_URL environment variable.",
        UserWarning
    )

limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=["100/minute", "1000/hour"],
    storage_uri=storage_uri,
    headers_enabled=True,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """速率限制超出处理器"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate Limit Exceeded",
            "detail": "API 调用频率超过限制，请稍后重试",
            "retry_after": exc.detail,
        },
        headers={
            "Retry-After": str(exc.detail)
        }
    )
