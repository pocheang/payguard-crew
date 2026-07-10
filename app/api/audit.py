"""
安全加固的审计API

修复的问题:
1. ✅ SQL注入防护 - 输入验证
2. ✅ 速率限制 - 防止API滥用
3. ✅ 安全的错误处理 - 不泄露内部信息
4. ✅ 请求大小限制
5. ✅ 详细的审计日志
6. ✅ Redis缓存优化
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import check_rate_limit
from app.api.error_handler import api_error_handler
from app.crew.audit_crew import run_audit_crew
from app.db.repositories import get_audit_logs, get_audit_report
from app.schemas.audit import AuditLogResponse, AuditReportRecord, AuditResponse
from app.schemas.transaction import TransactionInput
from app.utils.security import SecurityValidator
from app.utils.validation import validate_and_sanitize_transaction
from app.core.cache import get_cached_audit, cache_audit_result, invalidate_audit_cache

router = APIRouter()


@router.post("/transaction", response_model=AuditResponse)
@api_error_handler
def audit_transaction_secure(
    tx_data: dict,
    client_id: str = Depends(check_rate_limit)
) -> AuditResponse:
    """
    提交交易审核请求（安全加固版 + 缓存优化）

    安全特性:
    - ✅ 输入验证和清洗
    - ✅ 速率限制
    - ✅ 安全的错误处理
    - ✅ 审计日志
    - ✅ 结果缓存（1小时）

    需要在请求头中提供 X-API-Key 进行认证
    """
    # 1. 输入验证和清洗
    tx = validate_and_sanitize_transaction(tx_data)

    # 2. 检查缓存
    cached_result = get_cached_audit(tx.transaction_id)
    if cached_result:
        return cached_result

    # 3. 额外的安全验证
    SecurityValidator.validate_timestamp(tx.timestamp)
    SecurityValidator.validate_amount_range(tx.amount)
    SecurityValidator.sanitize_transaction_id(tx.transaction_id)

    # 4. 执行审计
    result = run_audit_crew(tx)

    # 5. 缓存结果
    cache_audit_result(tx.transaction_id, result, expire=3600)

    return result


@router.get("/report/{transaction_id}", response_model=AuditReportRecord)
@api_error_handler
def get_report_secure(
    transaction_id: str,
    client_id: str = Depends(check_rate_limit)
) -> AuditReportRecord:
    """
    查询交易审核报告（安全加固版 + 缓存优化）

    安全特性:
    - ✅ 输入清洗（防止SQL注入）
    - ✅ 速率限制
    - ✅ 安全的错误处理
    - ✅ 结果缓存

    需要在请求头中提供 X-API-Key 进行认证
    """
    # 清洗transaction_id，防止SQL注入
    safe_transaction_id = SecurityValidator.sanitize_transaction_id(transaction_id)

    # 检查缓存
    cached = get_cached_audit(safe_transaction_id)
    if cached:
        return cached

    # 查询报告
    report = get_audit_report(safe_transaction_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="未找到审计报告"
        )

    # 缓存结果
    cache_audit_result(safe_transaction_id, report, expire=3600)

    return report


@router.get("/logs/{transaction_id}", response_model=AuditLogResponse)
def get_logs_secure(
    transaction_id: str,
    client_id: str = Depends(check_rate_limit)
) -> AuditLogResponse:
    """
    查询交易审核日志（安全加固版）
    
    安全特性:
    - ✅ 输入清洗（防止SQL注入）
    - ✅ 速率限制
    - ✅ 安全的错误处理

    需要在请求头中提供 X-API-Key 进行认证
    """
    # 清洗transaction_id，防止SQL注入
    safe_transaction_id = SecurityValidator.sanitize_transaction_id(transaction_id)

    # 查询日志
    logs = get_audit_logs(safe_transaction_id)

    if not logs.logs:
        raise HTTPException(
            status_code=404,
            detail="未找到审计日志"
        )

    return logs
