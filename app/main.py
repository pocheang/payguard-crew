"""
FastAPI 应用主入口

模块化重构：
- app/core/lifecycle.py - 生命周期管理
- app/core/middlewares.py - 中间件配置
- app/core/exception_handlers.py - 异常处理
"""
import os

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.lifecycle import lifespan
from app.core.middlewares import configure_middlewares
from app.core.exception_handlers import (
    global_exception_handler,
    value_error_handler,
)
from app.middleware import limiter, rate_limit_exceeded_handler

# 导入所有API路由
from app.api.audit import router as audit_router
from app.api.batch import router as batch_router
from app.api.review import router as review_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.metrics import router as metrics_router


# 创建应用
app = FastAPI(
    title="PayGuard Crew",
    description="Enterprise Payment Risk Control & Compliance Audit System",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 配置速率限制
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# 配置中间件
configure_middlewares(app)

# 配置异常处理器
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

# 注册所有API路由（扁平化结构）
app.include_router(audit_router, prefix="/api/audit", tags=["audit"])
app.include_router(batch_router, prefix="/api/audit", tags=["batch-audit"])
app.include_router(review_router, prefix="/api/review", tags=["review-workflow"])
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])


@app.get("/")
def root() -> dict:
    """API 根路径"""
    settings = get_settings()
    return {
        "service": "payguard-crew",
        "version": "0.2.0",
        "environment": str(settings.app_env.value),
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "metrics": "/api/metrics",
            "audit": "/api/audit/transaction",
            "batch": "/api/audit/batch",
            "review": "/api/review/create",
        },
        "features": {
            "jwt_auth": True,
            "rbac": True,
            "distributed_tracing": os.getenv("OTEL_ENABLED", "false").lower() == "true",
            "error_tracking": bool(os.getenv("SENTRY_DSN")),
            "database": os.getenv("DATABASE_TYPE", "sqlite"),
            "rate_limiting": bool(os.getenv("REDIS_URL")),
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
