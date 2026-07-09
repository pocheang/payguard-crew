"""API错误处理装饰器和中间件"""
from functools import wraps
from typing import Callable, Any

from fastapi import HTTPException

from app.utils.security import safe_error_message


def api_error_handler(func: Callable) -> Callable:
    """
    API错误处理装饰器

    统一处理API路由中的异常：
    - HTTPException: 直接抛出（保持FastAPI原始行为）
    - ValueError: 转为400错误（客户端输入错误）
    - Exception: 转为500错误（服务器内部错误）

    使用safe_error_message确保不泄露敏感信息

    示例：
        @router.post("/endpoint")
        @api_error_handler
        def my_endpoint(data: dict):
            # 业务逻辑
            return result
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=safe_error_message(e, include_details=False)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=safe_error_message(e, include_details=False)
            )

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=safe_error_message(e, include_details=False)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=safe_error_message(e, include_details=False)
            )

    # 检测是否为异步函数
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
