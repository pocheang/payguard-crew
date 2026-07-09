"""
应用生命周期管理

包含：启动/关闭逻辑、初始化、健康检查
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    应用生命周期管理器

    启动时初始化所有服务
    """
    settings = get_settings()

    # 初始化数据库
    init_db()
    print("✅ Database initialized")

    # 初始化审核工作流表
    try:
        from app.db.schemas_review import init_review_tables
        init_review_tables()
    except Exception as e:
        print(f"⚠️ Review tables initialization failed: {e}")

    # 生产环境安全检查
    if settings.is_production:
        if not os.getenv("API_KEYS"):
            raise ValueError(
                "Production Error: API_KEYS must be configured"
            )

    # 验证JWT配置
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

    # 预热ChromaDB
    try:
        from app.rag.vector_store import get_vector_store
        get_vector_store()
        print("✅ ChromaDB warmed up")
    except Exception as e:
        print(f"⚠️ ChromaDB warmup failed: {e}")

    yield

    # 清理资源
    try:
        from app.db.database_engine import close_db_connections
        close_db_connections()
        print("✅ Database connections closed")
    except Exception:
        pass
