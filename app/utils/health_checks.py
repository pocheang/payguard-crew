"""
健康检查工具模块

提供各组件的健康检查逻辑
"""
from datetime import datetime
from pydantic import BaseModel
import time


class ComponentHealth(BaseModel):
    """组件健康状态"""
    status: str  # ok, degraded, error
    message: str | None = None
    latency_ms: float | None = None


def check_database() -> ComponentHealth:
    """检查数据库连接"""
    try:
        from app.db.database import get_connection

        start = time.perf_counter()
        with get_connection() as conn:
            conn.execute("SELECT 1")
        latency = (time.perf_counter() - start) * 1000

        return ComponentHealth(
            status="ok",
            message="SQLite connected",
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        return ComponentHealth(
            status="error",
            message=f"Database error: {str(e)}"
        )


def check_knowledge_base() -> ComponentHealth:
    """检查知识库目录"""
    from app.config import get_settings

    settings = get_settings()
    if settings.docs_dir.exists():
        doc_count = len(list(settings.docs_dir.glob("*.md")))
        return ComponentHealth(
            status="ok",
            message=f"{doc_count} documents available"
        )
    else:
        return ComponentHealth(
            status="error",
            message="Knowledge base directory not found"
        )


def check_rag_system() -> ComponentHealth:
    """检查 RAG 系统"""
    try:
        from app.rag.vector_store import get_vector_store

        store = get_vector_store()
        if store:
            return ComponentHealth(
                status="ok",
                message="Vector store initialized"
            )
        else:
            return ComponentHealth(
                status="degraded",
                message="Vector store not initialized, using fallback retriever"
            )
    except Exception as e:
        return ComponentHealth(
            status="degraded",
            message=f"RAG system degraded: {str(e)}"
        )


def check_llm_config() -> ComponentHealth:
    """检查 LLM 配置"""
    from app.config import get_settings

    settings = get_settings()
    if settings.llm_enabled:
        return ComponentHealth(
            status="ok",
            message=f"LLM enabled: {settings.llm_provider}/{settings.active_model}"
        )
    else:
        return ComponentHealth(
            status="ok",
            message="LLM disabled, using rule engine only"
        )


def get_overall_status(components: dict[str, ComponentHealth]) -> str:
    """计算整体健康状态"""
    error_count = sum(1 for c in components.values() if c.status == "error")
    degraded_count = sum(1 for c in components.values() if c.status == "degraded")

    if error_count > 0:
        return "error"
    elif degraded_count > 0:
        return "degraded"
    else:
        return "ok"
