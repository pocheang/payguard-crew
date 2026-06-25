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
from app.api.auth import router as auth_router
from app.api.v1 import api_v1_router, legacy_router
from app.config import get_settings
from app.db.database import init_db
from app.middleware import limiter, rate_limit_exceeded_handler, RequestIDMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager with enterprise initialization."""
    settings = get_settings()

    # 初始化数据库
    init_db()
    print("✅ Database initialized")

    # 🔒 安全检查：生产环境必须配置关键安全参数
    if settings.app_env in ["prod", "production"]:
        if not os.getenv("API_KEYS"):
            import warnings
            warnings.warn(
                "⚠️ 生产环境未配置 API_KEYS，API 未受保护！",
                UserWarning,
                stacklevel=2
            )

        # 验证 JWT 配置
        try:
            from app.core.auth import validate_jwt_config
            validate_jwt_config()
            print("✅ JWT configuration validated")
        except Exception as e:
            print(f"⚠️ JWT configuration error: {e}")

    # 初始化结构化日志
    try:
        from app.core.logging import setup_logging
        setup_logging()
        print("✅ Structured logging initialized")
    except Exception as e:
        print(f"⚠️ Logging initialization failed: {e}")

    # 初始化分布式追踪
    try:
        from app.core.tracing import setup_tracing
        setup_tracing(app)
    except Exception as e:
        print(f"⚠️ Tracing initialization failed: {e}")

    # 初始化错误追踪
    try:
        from app.core.monitoring import setup_sentry
        setup_sentry(app)
    except Exception as e:
        print(f"⚠️ Sentry initialization failed: {e}")

    # 🚀 优化：预热 ChromaDB 向量库（消除冷启动延迟）
    try:
        from app.rag.vector_store import get_vector_store
        get_vector_store()
        print("✅ ChromaDB warmed up")
    except Exception as e:
        print(f"⚠️ ChromaDB warmup failed: {e}")

    yield

    # Cleanup on shutdown
    try:
        from app.db.database_engine import close_db_connections
        close_db_connections()
        print("✅ Database connections closed")
    except Exception:
        # 空实现
app = FastAPI(
    title="PayGuard Crew",
    description="Enterprise Payment Risk Control & Compliance Audit System",
    version="0.2.0",
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
    # 获取或生成请求 ID
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # 记录完整错误到日志
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
        # 日志记录失败，使用 print
        print(f"ERROR [request_id={request_id}]: {exc}")

    # 发送错误到 Sentry
    try:
        from app.core.monitoring import capture_exception
        capture_exception(exc, context={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method
        })
    except Exception:
        # 空实现
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


# API v1 routes (recommended)
app.include_router(api_v1_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

# Legacy routes (backward compatibility)
app.include_router(legacy_router)
app.include_router(auth_router, tags=["authentication"])


@app.get("/")
def root() -> dict:
    """API 根路径"""
    return {
        "service": "payguard-crew",
        "version": "0.2.0",
        "environment": get_settings().app_env,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "features": {
            "jwt_auth": True,
            "rbac": True,
            "distributed_tracing": os.getenv("OTEL_ENABLED", "false").lower() == "true",
            "error_tracking": bool(os.getenv("SENTRY_DSN")),
            "database": os.getenv("DATABASE_TYPE", "sqlite")
        }
    }
