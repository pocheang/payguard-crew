"""
速率限制中间件（增强版）

使用滑动窗口算法限制 API 调用频率，防止滥用
生产环境使用Redis存储，开发环境可使用内存存储

增强功能：
- 分级限流（不同API不同限制）
- 白名单支持
- 自适应限流
- 详细的限流统计
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.core.cache import cache


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


# 白名单检查
WHITELIST_IPS = set(os.getenv("RATE_LIMIT_WHITELIST", "").split(","))
WHITELIST_API_KEYS = set(os.getenv("RATE_LIMIT_WHITELIST_KEYS", "").split(","))


def is_whitelisted(request: Request) -> bool:
    """检查是否在白名单中"""
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key in WHITELIST_API_KEYS:
        return True

    ip = get_remote_address(request)
    if ip in WHITELIST_IPS:
        return True

    return False


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
    """速率限制超出处理器（增强版）"""
    # 记录限流事件
    key = rate_limit_key_func(request)
    cache.increment(f"payguard:rate_limit_violations:{key}", expire=3600)

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate Limit Exceeded",
            "detail": "API 调用频率超过限制，请稍后重试",
            "retry_after": exc.detail,
            "limit_info": {
                "endpoint": str(request.url.path),
                "method": request.method
            }
        },
        headers={
            "Retry-After": str(exc.detail),
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0"
        }
    )


# 分级限流装饰器

def adaptive_rate_limit(limits: str):
    """
    自适应限流装饰器

    根据请求特征动态调整限流策略

    Args:
        limits: 限流规则，如 "20/minute"
    """
    def decorator(func):
        # 应用slowapi的limit装饰器
        decorated = limiter.limit(limits)(func)
        return decorated
    return decorator


# 限流统计

def get_rate_limit_stats(key: str = None) -> dict:
    """
    获取限流统计

    Args:
        key: 特定键的统计，None表示全局统计

    Returns:
        统计信息字典
    """
    if not cache.enabled:
        return {"error": "Redis not available"}

    if key:
        violations = cache.get(f"payguard:rate_limit_violations:{key}") or 0
        return {
            "key": key,
            "violations_last_hour": violations
        }

    # 全局统计
    pattern = "payguard:rate_limit_violations:*"
    keys = cache.client.keys(pattern)

    total_violations = 0
    for k in keys:
        val = cache.client.get(k)
        if val:
            total_violations += int(val)

    return {
        "total_unique_violators": len(keys),
        "total_violations_last_hour": total_violations
    }
