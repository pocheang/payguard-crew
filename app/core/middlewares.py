"""
应用中间件配置

包含：安全头、请求ID、CORS等中间件
"""
import os
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""

    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

    async def dispatch(self, request, call_next):
        # 检查请求大小
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request Entity Too Large",
                    "detail": "Request body exceeds 10MB limit"
                }
            )

        response = await call_next(request)

        # 完整的安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        return response


def configure_middlewares(app: FastAPI) -> None:
    """
    配置所有中间件

    顺序很重要：从上到下执行
    """
    from app.middleware import RequestIDMiddleware

    # 1. 请求ID中间件
    app.add_middleware(RequestIDMiddleware)

    # 2. 安全头中间件
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. CORS中间件（可选）
    cors_origins_str = os.getenv("CORS_ORIGINS", "")
    if cors_origins_str:
        cors_origins = [
            origin.strip()
            for origin in cors_origins_str.split(",")
            if origin.strip()
        ]

        # 安全检查
        if "*" in cors_origins:
            raise ValueError(
                "Security Error: Wildcard CORS origins ('*') not allowed with credentials"
            )

        # 验证URL格式
        for origin in cors_origins:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"Security Error: Invalid CORS origin '{origin}'"
                )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],
            max_age=600,
        )
