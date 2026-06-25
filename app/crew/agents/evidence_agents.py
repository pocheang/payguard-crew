"""
Evidence and report agents - RAG and Report generation
"""
from time import perf_counter
from typing import Optional

from app.config import get_settings
from app.schemas.audit import AuditLogEntry
from app.schemas.transaction import TransactionInput
from app.rag.retriever import AuditEvidenceRetriever
from app.rules.risk_rules import build_rule_query
from app.agents.llm_client import generate_audit_narrative
from app.crew.crewai_runner import run_crewai_json_task_async
from app.crew.parsers import parse_evidence_summary, parse_report_payload
from app.crew.fallbacks import build_fallback_summary, build_fallback_suggestion
from app.crew.utils import log_status


async def run_rag_agent(
    rule_result: dict, tx: TransactionInput, registry: dict, attempted_crewai: bool
) -> tuple[list, Optional[str], dict, AuditLogEntry]:
    """RAG Evidence Agent - 检索证据"""
    settings = get_settings()
    started = perf_counter()

    query = build_rule_query(rule_result["triggered_rules"], tx)
    evidence = AuditEvidenceRetriever().retrieve(
        query=query,
        top_k=settings.rag_top_k,
    )

    rag_payload, rag_llm_ms, rag_error = await run_crewai_json_task_async(
        registry["rag_evidence_agent"],
        {
            "query": query,
            "evidence": [item.model_dump() for item in evidence],
        },
    )
    evidence_summary = parse_evidence_summary(rag_payload)
    if rag_payload and evidence_summary is None:
        rag_error = rag_error or "CrewAI payload missing evidence summary"

    rag_output = {
        "backend": "crewai" if evidence_summary else "local",
        "evidence": [item.model_dump() for item in evidence],
        "evidence_summary": evidence_summary,
    }

    log_entry = AuditLogEntry(
        agent_name="rag_evidence_agent",
        input_data=str({"query": query}),
        output_data=str(rag_output),
        status=log_status(rag_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + rag_llm_ms,
        error_message=rag_error,
        created_at=None,
    )

    return evidence, evidence_summary, rag_output, log_entry


async def run_report_agent(
    tx_payload: dict,
    rule_result: dict,
    transaction_output: dict,
    compliance_output: dict,
    evidence: list,
    evidence_summary: Optional[str],
    registry: dict,
    attempted_crewai: bool,
) -> tuple[dict, str, AuditLogEntry]:
    """Report Agent - 生成报告"""
    settings = get_settings()
    started = perf_counter()

    report_payload, report_llm_ms, report_error = await run_crewai_json_task_async(
        registry["report_agent"],
        {
            "transaction": tx_payload,
            "rule_result": rule_result,
            "transaction_findings": transaction_output,
            "compliance_result": compliance_output,
            "evidence": [item.model_dump() for item in evidence],
            "evidence_summary": evidence_summary,
        },
    )
    narrative = parse_report_payload(report_payload)
    report_backend = "crewai" if narrative else "local"

    # Fallback 逻辑
    if narrative is None:
        llm_narrative = generate_audit_narrative(
            {
                "transaction": tx_payload,
                "rule_result": rule_result,
                "evidence": [item.model_dump() for item in evidence],
                "transaction_findings": transaction_output,
                "compliance_result": compliance_output,
                "evidence_summary": evidence_summary,
            }
        )
        if llm_narrative is not None:
            narrative = llm_narrative
            report_backend = f"llm:{settings.llm_provider}"
        else:
            narrative = {
                "summary": build_fallback_summary(
                    rule_result,
                    transaction_output["transaction_findings"],
                    compliance_output["compliance_notes"],
                    evidence_summary,
                ),
                "suggestion": build_fallback_suggestion(rule_result),
            }
            report_backend = "local"

    report_output = {"backend": report_backend, **narrative}

    log_entry = AuditLogEntry(
        agent_name="report_agent",
        input_data=str({
            "transaction": tx_payload,
            "rule_result": rule_result,
            "transaction_result": transaction_output,
            "compliance_result": compliance_output,
            "evidence": [item.model_dump() for item in evidence],
            "evidence_summary": evidence_summary,
        }),
        output_data=str(report_output),
        status=log_status(report_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + report_llm_ms,
        error_message=report_error,
        created_at=None,
    )

    return narrative, report_backend, log_entry
