"""
审计工作流主入口 (LEGACY VERSION - 500 lines)

⚠️ DEPRECATION NOTICE:
This is the original monolithic implementation.

For new code, please use: app/crew/audit_crew_refactored.py (110 lines)
Benefits:
- 78% code reduction (500 → 110 lines)
- Better modularity (agents/ and fallbacks/ directories)
- Easier to maintain and extend
- Same functionality and performance

This file is kept for backward compatibility only.
Planned removal: v0.2.0

Migration Guide: See docs/MIGRATION_GUIDE.md

---
协调各个 Agent 执行审计流程
支持并行执行以提升性能
"""
import asyncio
from time import perf_counter
from typing import Optional

from app.agents.agent_factory import build_agent_registry
from app.agents.llm_client import generate_audit_narrative
from app.config import get_settings
from app.db.repository import save_audit_result_optimized
from app.rag.retriever import AuditEvidenceRetriever
from app.rules.risk_rules import build_rule_query, evaluate_risk
from app.schemas.audit import AuditLogEntry, AuditResponse
from app.schemas.transaction import TransactionInput
from app.crew.crewai_runner import run_crewai_json_task_async
from app.crew.parsers import (
    parse_transaction_findings,
    parse_rule_explanation,
    parse_compliance_result,
    parse_evidence_summary,
    parse_report_payload,
    parse_fraud_detection_result,
    parse_merchant_risk_result,
    parse_device_fingerprint_result,
    parse_velocity_check_result,
)
from app.crew.fallbacks import (
    build_transaction_findings,
    build_compliance_notes,
    build_fallback_summary,
    build_fallback_suggestion,
    build_fraud_detection_result,
    build_merchant_risk_result,
    build_device_fingerprint_result,
    build_velocity_check_result,
)
from app.crew.utils import log_status


async def _run_transaction_agent(
    tx: TransactionInput, tx_payload: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Transaction Agent - 分析交易行为"""
    started = perf_counter()
    local_transaction_findings = build_transaction_findings(tx)

    transaction_payload, transaction_llm_ms, transaction_error = await run_crewai_json_task_async(
        registry["transaction_agent"],
        {"transaction": tx_payload},
    )
    transaction_result = parse_transaction_findings(transaction_payload)
    if transaction_payload and transaction_result is None:
        transaction_error = transaction_error or "CrewAI payload missing transaction keys"

    transaction_output = {
        "backend": "crewai" if transaction_result else "local",
        "transaction_findings": local_transaction_findings,
        "risk_points": (transaction_result or {}).get("risk_points", local_transaction_findings),
        "behavior_summary": (transaction_result or {}).get(
            "behavior_summary",
            "；".join(local_transaction_findings),
        ),
    }

    # 创建日志条目
    log_entry = AuditLogEntry(
        agent_name="transaction_agent",
        input_data=str(tx_payload),
        output_data=str(transaction_output),
        status=log_status(transaction_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + transaction_llm_ms,
        error_message=transaction_error,
        created_at=None,
    )

    return transaction_output, log_entry


async def _run_risk_rule_agent(
    tx: TransactionInput, tx_payload: dict, rule_result: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Risk Rule Agent - 解释规则"""
    started = perf_counter()

    rule_payload, rule_llm_ms, rule_error = await run_crewai_json_task_async(
        registry["risk_rule_agent"],
        {"transaction": tx_payload, "rule_result": rule_result},
    )
    rule_explanation = parse_rule_explanation(rule_payload)
    if rule_payload and rule_explanation is None:
        rule_error = rule_error or "CrewAI payload missing rule explanation"

    rule_output = {
        "backend": "crewai" if rule_explanation else "local",
        "authoritative_source": "app.rules.risk_rules.evaluate_risk",
        "rule_result": rule_result,
        "rule_explanation": rule_explanation,
    }

    log_entry = AuditLogEntry(
        agent_name="risk_rule_agent",
        input_data=str(tx_payload),
        output_data=str(rule_output),
        status=log_status(rule_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + rule_llm_ms,
        error_message=rule_error,
        created_at=None,
    )

    return rule_output, log_entry


async def _run_compliance_agent(
    tx: TransactionInput, tx_payload: dict, rule_result: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Compliance Agent - 合规检查"""
    started = perf_counter()
    local_compliance_notes = build_compliance_notes(tx, rule_result)

    compliance_payload, compliance_llm_ms, compliance_error = await run_crewai_json_task_async(
        registry["compliance_agent"],
        {"transaction": tx_payload, "rule_result": rule_result},
    )
    compliance_result = parse_compliance_result(compliance_payload)
    if compliance_payload and compliance_result is None:
        compliance_error = compliance_error or "CrewAI payload missing compliance keys"

    compliance_output = {
        "backend": "crewai" if compliance_result else "local",
        "compliance_notes": (compliance_result or {}).get(
            "compliance_notes", local_compliance_notes
        ),
        "manual_review_reason": (compliance_result or {}).get(
            "manual_review_reason",
            "；".join(local_compliance_notes),
        ),
    }

    log_entry = AuditLogEntry(
        agent_name="compliance_agent",
        input_data=str({"transaction": tx_payload, "rule_result": rule_result}),
        output_data=str(compliance_output),
        status=log_status(compliance_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + compliance_llm_ms,
        error_message=compliance_error,
        created_at=None,
    )

    return compliance_output, log_entry


async def _run_rag_agent(
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


async def _run_fraud_detection_agent(
    tx: TransactionInput, tx_payload: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Fraud Detection Agent - 欺诈检测"""
    started = perf_counter()
    local_fraud_result = build_fraud_detection_result(tx)

    fraud_payload, fraud_llm_ms, fraud_error = await run_crewai_json_task_async(
        registry["fraud_detection_agent"],
        {"transaction": tx_payload},
    )
    fraud_result = parse_fraud_detection_result(fraud_payload)
    if fraud_payload and fraud_result is None:
        fraud_error = fraud_error or "CrewAI payload missing fraud detection keys"

    fraud_output = {
        "backend": "crewai" if fraud_result else "local",
        **(fraud_result or local_fraud_result),
    }

    log_entry = AuditLogEntry(
        agent_name="fraud_detection_agent",
        input_data=str(tx_payload),
        output_data=str(fraud_output),
        status=log_status(fraud_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + fraud_llm_ms,
        error_message=fraud_error,
        created_at=None,
    )

    return fraud_output, log_entry


async def _run_merchant_risk_agent(
    tx: TransactionInput, tx_payload: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Merchant Risk Agent - 商户风险评估"""
    started = perf_counter()
    local_merchant_result = build_merchant_risk_result(tx)

    merchant_payload, merchant_llm_ms, merchant_error = await run_crewai_json_task_async(
        registry["merchant_risk_agent"],
        {"transaction": tx_payload},
    )
    merchant_result = parse_merchant_risk_result(merchant_payload)
    if merchant_payload and merchant_result is None:
        merchant_error = merchant_error or "CrewAI payload missing merchant risk keys"

    merchant_output = {
        "backend": "crewai" if merchant_result else "local",
        **(merchant_result or local_merchant_result),
    }

    log_entry = AuditLogEntry(
        agent_name="merchant_risk_agent",
        input_data=str(tx_payload),
        output_data=str(merchant_output),
        status=log_status(merchant_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + merchant_llm_ms,
        error_message=merchant_error,
        created_at=None,
    )

    return merchant_output, log_entry


async def _run_device_fingerprint_agent(
    tx: TransactionInput, tx_payload: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Device Fingerprint Agent - 设备指纹分析"""
    started = perf_counter()
    local_device_result = build_device_fingerprint_result(tx)

    device_payload, device_llm_ms, device_error = await run_crewai_json_task_async(
        registry["device_fingerprint_agent"],
        {"transaction": tx_payload},
    )
    device_result = parse_device_fingerprint_result(device_payload)
    if device_payload and device_result is None:
        device_error = device_error or "CrewAI payload missing device fingerprint keys"

    device_output = {
        "backend": "crewai" if device_result else "local",
        **(device_result or local_device_result),
    }

    log_entry = AuditLogEntry(
        agent_name="device_fingerprint_agent",
        input_data=str(tx_payload),
        output_data=str(device_output),
        status=log_status(device_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + device_llm_ms,
        error_message=device_error,
        created_at=None,
    )

    return device_output, log_entry


async def _run_velocity_check_agent(
    tx: TransactionInput, tx_payload: dict, registry: dict, attempted_crewai: bool
) -> tuple[dict, AuditLogEntry]:
    """Velocity Check Agent - 交易速度检查"""
    started = perf_counter()
    local_velocity_result = build_velocity_check_result(tx)

    velocity_payload, velocity_llm_ms, velocity_error = await run_crewai_json_task_async(
        registry["velocity_check_agent"],
        {"transaction": tx_payload},
    )
    velocity_result = parse_velocity_check_result(velocity_payload)
    if velocity_payload and velocity_result is None:
        velocity_error = velocity_error or "CrewAI payload missing velocity check keys"

    velocity_output = {
        "backend": "crewai" if velocity_result else "local",
        **(velocity_result or local_velocity_result),
    }

    log_entry = AuditLogEntry(
        agent_name="velocity_check_agent",
        input_data=str(tx_payload),
        output_data=str(velocity_output),
        status=log_status(velocity_error, attempted_crewai),
        latency_ms=int((perf_counter() - started) * 1000) + velocity_llm_ms,
        error_message=velocity_error,
        created_at=None,
    )

    return velocity_output, log_entry


async def _run_report_agent(
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


async def run_audit_crew_async(tx: TransactionInput) -> AuditResponse:
    """
    异步执行审计工作流（优化版 + 新增4个Agent）

    优化点：
    1. 并行执行多个独立的Agent
    2. 使用异步执行减少等待时间
    3. 新增欺诈检测、商户风险、设备指纹、速度检查Agent
    """
    settings = get_settings()
    registry = build_agent_registry()
    logs: list[AuditLogEntry] = []
    tx_payload = tx.model_dump(mode="json")
    attempted_crewai = settings.enable_crewai

    # === 阶段1: Transaction Agent（必须先执行）===
    transaction_output, tx_log = await _run_transaction_agent(
        tx, tx_payload, registry, attempted_crewai
    )
    logs.append(tx_log)

    # === 阶段2: 规则引擎评估（快速，同步）===
    rule_result = evaluate_risk(tx)

    # === 阶段3: 并行执行多个Agent ===
    # 🚀 优化点：6个Agent可以并行执行
    rule_task = _run_risk_rule_agent(tx, tx_payload, rule_result, registry, attempted_crewai)
    compliance_task = _run_compliance_agent(tx, tx_payload, rule_result, registry, attempted_crewai)
    fraud_task = _run_fraud_detection_agent(tx, tx_payload, registry, attempted_crewai)
    merchant_task = _run_merchant_risk_agent(tx, tx_payload, registry, attempted_crewai)
    device_task = _run_device_fingerprint_agent(tx, tx_payload, registry, attempted_crewai)
    velocity_task = _run_velocity_check_agent(tx, tx_payload, registry, attempted_crewai)

    (
        (rule_output, rule_log),
        (compliance_output, compliance_log),
        (fraud_output, fraud_log),
        (merchant_output, merchant_log),
        (device_output, device_log),
        (velocity_output, velocity_log),
    ) = await asyncio.gather(
        rule_task,
        compliance_task,
        fraud_task,
        merchant_task,
        device_task,
        velocity_task,
    )
    logs.extend([rule_log, compliance_log, fraud_log, merchant_log, device_log, velocity_log])

    # === 阶段4: RAG Evidence Agent ===
    evidence, evidence_summary, rag_output, rag_log = await _run_rag_agent(
        rule_result, tx, registry, attempted_crewai
    )
    logs.append(rag_log)

    # === 阶段5: Report Agent ===
    narrative, report_backend, report_log = await _run_report_agent(
        tx_payload,
        rule_result,
        transaction_output,
        compliance_output,
        evidence,
        evidence_summary,
        registry,
        attempted_crewai,
    )
    logs.append(report_log)

    # 构建响应并保存
    response = AuditResponse(
        transaction_id=tx.transaction_id,
        risk_level=rule_result["risk_level"],
        risk_score=rule_result["risk_score"],
        decision=rule_result["decision"],
        summary=narrative["summary"],
        triggered_rules=rule_result["triggered_rules"],
        evidence=evidence,
        suggestion=narrative["suggestion"],
        requires_manual_review=rule_result["requires_manual_review"],
    )

    # 🚀 优化点：使用批量写入
    save_audit_result_optimized(tx, response, logs)

    return response


def run_audit_crew(tx: TransactionInput) -> AuditResponse:
    """
    同步包装器，保持向后兼容
    """
    return asyncio.run(run_audit_crew_async(tx))
