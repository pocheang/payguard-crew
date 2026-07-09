"""
全局异常处理器

统一处理应用异常
"""
import uuid

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.config import get_settings


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 记录完整错误
    try:
        from app.core.logging import get_logger
        logger = get_logger("api")
        logger.error(
            f"Unhandled exception [request_id={request_id}]: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": str(request.url.path),
                "method": request.method,
                "error_type": type(exc).__name__
            },
            exc_info=True
        )
    except Exception:
        print(f"ERROR [request_id={request_id}]: {exc}")

    # 发送到Sentry
    try:
        from app.core.monitoring import capture_exception
        capture_exception(exc, context={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method
        })
    except Exception:
        pass

    settings = get_settings()
    error_detail = str(exc) if settings.is_development else "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
            "request_id": request_id,
            "path": str(request.url.path),
        }
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """值错误处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "path": str(request.url.path),
        }
    )
