"""
请求 ID 中间件

为每个请求生成唯一的追踪 ID，便于日志关联和问题排查
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求添加唯一的 Request ID"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 生成或获取 Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 将 Request ID 添加到请求状态，便于在路由中访问
        request.state.request_id = request_id

        # 调用下一个中间件/路由
        response = await call_next(request)

        # 在响应头中返回 Request ID
        response.headers["X-Request-ID"] = request_id

        return response
