"""
Core agent runners - Transaction, Risk Rule, Compliance
"""
from time import perf_counter

from app.schemas.audit import AuditLogEntry
from app.schemas.transaction import TransactionInput
from app.crew.crewai_runner import run_crewai_json_task_async
from app.crew.parsers import (
    parse_transaction_findings,
    parse_rule_explanation,
    parse_compliance_result,
)
from app.crew.fallbacks import (
    build_transaction_findings,
    build_compliance_notes,
)
from app.crew.utils import log_status


async def run_transaction_agent(
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


async def run_risk_rule_agent(
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


async def run_compliance_agent(
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
