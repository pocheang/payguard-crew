"""
速率限制中间件

使用滑动窗口算法限制 API 调用频率，防止滥用
"""
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
limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=["100/minute", "1000/hour"],
    storage_uri="memory://",
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
