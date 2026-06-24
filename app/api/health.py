"""
健康检查 API

提供详细的系统健康状态，包括数据库、RAG、LLM 等组件
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

from app.utils.health_checks import (
    ComponentHealth,
    check_database,
    check_knowledge_base,
    check_rag_system,
    check_llm_config,
    get_overall_status
)

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str  # ok, degraded, error
    version: str
    timestamp: str
    environment: str
    components: dict[str, ComponentHealth]


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """详细健康检查"""
    from app.config import get_settings

    settings = get_settings()

    # 执行各组件检查
    components = {
        "database": check_database(),
        "knowledge_base": check_knowledge_base(),
        "rag": check_rag_system(),
        "llm": check_llm_config()
    }

    return HealthResponse(
        status=get_overall_status(components),
        version="0.1.1",
        timestamp=datetime.utcnow().isoformat() + "Z",
        environment=settings.app_env,
        components=components
    )


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_check() -> dict:
    """
    存活检查（Kubernetes liveness probe）

    仅检查进程是否运行，不检查依赖
    """
    return {"status": "ok"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_check() -> dict:
    """
    就绪检查（Kubernetes readiness probe）

    检查是否可以处理请求
    """
    from app.config import get_settings

    try:
        settings = get_settings()

        # 检查数据库连接
        db_health = check_database()
        if db_health.status == "error":
            return {"status": "not_ready", "reason": db_health.message}

        # 检查知识库目录
        if not settings.docs_dir.exists():
            return {"status": "not_ready", "reason": "knowledge base not found"}

        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}
