import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.audit import router as audit_router
from app.api.health import router as health_router
from app.api.metrics import router as metrics_router
from app.config import get_settings
from app.db.database import init_db
from app.middleware import limiter, rate_limit_exceeded_handler, RequestIDMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 初始化数据库
    init_db()

    # 验证配置（会在配置错误时抛出异常）
    settings = get_settings()

    # 🔒 安全检查：生产环境必须配置 API_KEYS
    if settings.app_env in ["prod", "production"] and not os.getenv("API_KEYS"):
        import warnings
        warnings.warn(
            "⚠️ 生产环境未配置 API_KEYS，API 未受保护！",
            UserWarning,
            stacklevel=2
        )

    # 🚀 优化：预热 ChromaDB 向量库（消除冷启动延迟）
    try:
        from app.rag.vector_store import get_vector_store
        get_vector_store()  # 预加载
        print("✅ ChromaDB 预热完成")
    except Exception as e:
        print(f"⚠️ ChromaDB 预热失败: {e}")

    yield


app = FastAPI(
    title="PayGuard Crew",
    description="Payment risk and compliance audit AI Agent demo",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 绑定限流器到 FastAPI 应用
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# 🔒 安全响应头中间件
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全响应头"""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


# 添加中间件（顺序很重要：从上到下执行）
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS 配置（可选，用于前端集成）
settings = get_settings()
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
if cors_origins and cors_origins[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# 全局异常处理器（改进版）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    # 生成请求 ID 用于追踪
    request_id = str(uuid.uuid4())

    # 记录完整错误到日志
    try:
        from app.utils.logger import logger
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
        # 日志记录失败，使用 print
        print(f"ERROR [request_id={request_id}]: {exc}")

    settings = get_settings()

    # 仅在明确的开发环境显示详细错误
    is_dev = settings.app_env in ["dev", "development", "local"]
    error_detail = str(exc) if is_dev else "服务器内部错误，请联系管理员"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
            "request_id": request_id,
            "path": str(request.url.path),
        }
    )


@app.exception_handler(ValueError)
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


app.include_router(audit_router, prefix="/audit", tags=["audit"])
app.include_router(health_router, tags=["health"])
app.include_router(metrics_router, tags=["metrics"])


@app.get("/")
def root() -> dict:
    """API 根路径"""
    return {
        "service": "payguard-crew",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }
