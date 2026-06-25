"""
Risk detection agents - Fraud, Merchant, Device, Velocity
"""
from time import perf_counter

from app.schemas.audit import AuditLogEntry
from app.schemas.transaction import TransactionInput
from app.crew.crewai_runner import run_crewai_json_task_async
from app.crew.parsers import (
    parse_fraud_detection_result,
    parse_merchant_risk_result,
    parse_device_fingerprint_result,
    parse_velocity_check_result,
)
from app.crew.fallbacks import (
    build_fraud_detection_result,
    build_merchant_risk_result,
    build_device_fingerprint_result,
    build_velocity_check_result,
)
from app.crew.utils import log_status


async def run_fraud_detection_agent(
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


async def run_merchant_risk_agent(
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


async def run_device_fingerprint_agent(
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


async def run_velocity_check_agent(
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
