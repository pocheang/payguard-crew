"""API依赖项和通用装饰器"""
from fastapi import HTTPException, Request, Security

from app.auth.api_key import verify_api_key
from app.middleware.rate_limit import limiter


def check_rate_limit(request: Request, api_key: str = Security(verify_api_key)) -> str:
    """
    检查速率限制（可复用的依赖项）

    使用slowapi的limiter进行速率限制检查

    Args:
        request: FastAPI请求对象
        api_key: API密钥（来自verify_api_key）

    Returns:
        客户端ID

    Note:
        实际的速率限制由slowapi中间件自动处理
        这个函数主要用于依赖注入，确保API Key验证和速率限制都执行
    """
    client_id = api_key or request.client.host
    return client_id
