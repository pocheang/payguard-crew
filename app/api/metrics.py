"""
Prometheus 监控指标 API

提供系统性能指标，用于 Grafana 可视化和告警
"""
from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

router = APIRouter()

# 定义指标
audit_requests_total = Counter(
    "payguard_audit_requests_total",
    "Total number of audit requests",
    ["risk_level", "decision"]
)

audit_request_duration_seconds = Histogram(
    "payguard_audit_request_duration_seconds",
    "Audit request duration in seconds",
    ["endpoint"]
)

triggered_rules_total = Counter(
    "payguard_triggered_rules_total",
    "Total number of triggered rules",
    ["rule_id", "rule_name"]
)

active_api_keys = Gauge(
    "payguard_active_api_keys",
    "Number of active API keys"
)

llm_requests_total = Counter(
    "payguard_llm_requests_total",
    "Total number of LLM requests",
    ["provider", "status"]
)

llm_request_duration_seconds = Histogram(
    "payguard_llm_request_duration_seconds",
    "LLM request duration in seconds",
    ["provider"]
)

rag_retrieval_total = Counter(
    "payguard_rag_retrieval_total",
    "Total number of RAG retrievals",
    ["backend"]
)

database_connections = Gauge(
    "payguard_database_connections",
    "Number of active database connections"
)


@router.get("/metrics")
def metrics() -> Response:
    """
    Prometheus metrics endpoint

    使用方式：
    1. 在 Prometheus 配置中添加此端点
    2. 在 Grafana 中创建仪表板可视化指标
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
