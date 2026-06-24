"""
监控指标工具模块

提供便捷的方法来记录 Prometheus 指标
"""
from app.api.metrics import (
    audit_requests_total,
    audit_request_duration_seconds,
    triggered_rules_total,
    llm_requests_total,
    llm_request_duration_seconds,
    rag_retrieval_total,
)
import time
from contextlib import contextmanager
from typing import Generator


def record_audit_request(risk_level: str, decision: str) -> None:
    """记录审计请求"""
    audit_requests_total.labels(risk_level=risk_level, decision=decision).inc()


def record_triggered_rule(rule_id: str, rule_name: str) -> None:
    """记录触发的规则"""
    triggered_rules_total.labels(rule_id=rule_id, rule_name=rule_name).inc()


def record_llm_request(provider: str, status: str) -> None:
    """记录 LLM 请求"""
    llm_requests_total.labels(provider=provider, status=status).inc()


def record_rag_retrieval(backend: str) -> None:
    """记录 RAG 检索"""
    rag_retrieval_total.labels(backend=backend).inc()


@contextmanager
def time_audit_request(endpoint: str) -> Generator[None, None, None]:
    """测量审计请求耗时

    使用方式:
        with time_audit_request("transaction"):
            # 执行审计逻辑
            pass
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        audit_request_duration_seconds.labels(endpoint=endpoint).observe(duration)


@contextmanager
def time_llm_request(provider: str) -> Generator[None, None, None]:
    """测量 LLM 请求耗时

    使用方式:
        with time_llm_request("deepseek"):
            # 执行 LLM 调用
            pass
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        llm_request_duration_seconds.labels(provider=provider).observe(duration)
