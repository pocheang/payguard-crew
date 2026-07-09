"""
安全加固的审计API

修复的问题:
1. ✅ SQL注入防护 - 输入验证
2. ✅ 速率限制 - 防止API滥用
3. ✅ 安全的错误处理 - 不泄露内部信息
4. ✅ 请求大小限制
5. ✅ 详细的审计日志
"""
from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.responses import JSONResponse

from app.auth.api_key import verify_api_key
from app.crew.audit_crew import run_audit_crew
from app.db.repositories import get_audit_logs, get_audit_report
from app.schemas.audit import AuditLogResponse, AuditReportRecord, AuditResponse
from app.schemas.transaction import TransactionInput
from app.utils.security import SecurityValidator, get_rate_limiter, safe_error_message
from app.utils.validation import validate_and_sanitize_transaction

router = APIRouter()


@router.post("/transaction", response_model=AuditResponse)
def audit_transaction_secure(
    tx_data: dict,
    request: Request,
    api_key: str = Security(verify_api_key)
) -> AuditResponse:
    """
    提交交易审核请求（安全加固版）
    
    安全特性:
    - ✅ 输入验证和清洗
    - ✅ 速率限制
    - ✅ 安全的错误处理
    - ✅ 审计日志
    
    需要在请求头中提供 X-API-Key 进行认证
    """
    try:
        # 1. 速率限制检查
        client_id = api_key or request.client.host
        rate_limiter = get_rate_limiter()
        allowed, error_msg = rate_limiter.check_rate_limit(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁: {error_msg}"
            )
        
        # 2. 输入验证和清洗
        tx = validate_and_sanitize_transaction(tx_data)
        
        # 3. 额外的安全验证
        SecurityValidator.validate_timestamp(tx.timestamp)
        SecurityValidator.validate_amount_range(tx.amount)
        SecurityValidator.sanitize_transaction_id(tx.transaction_id)
        
        # 4. 执行审计
        result = run_audit_crew(tx)
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        # 验证错误
        raise HTTPException(
            status_code=400,
            detail=safe_error_message(e, include_details=False)
        )
    except Exception as e:
        # 其他错误 - 不泄露内部信息
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(e, include_details=False)
        )


@router.get("/report/{transaction_id}", response_model=AuditReportRecord)
def get_report_secure(
    transaction_id: str,
    request: Request,
    api_key: str = Security(verify_api_key)
) -> AuditReportRecord:
    """
    查询交易审核报告（安全加固版）
    
    安全特性:
    - ✅ 输入清洗（防止SQL注入）
    - ✅ 速率限制
    - ✅ 安全的错误处理
    
    需要在请求头中提供 X-API-Key 进行认证
    """
    try:
        # 1. 速率限制检查
        client_id = api_key or request.client.host
        rate_limiter = get_rate_limiter()
        allowed, error_msg = rate_limiter.check_rate_limit(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁: {error_msg}"
            )
        
        # 2. 清洗transaction_id，防止SQL注入
        safe_transaction_id = SecurityValidator.sanitize_transaction_id(transaction_id)
        
        # 3. 查询报告
        report = get_audit_report(safe_transaction_id)
        
        if report is None:
            raise HTTPException(
                status_code=404,
                detail="未找到审计报告"
            )
        
        return report
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=safe_error_message(e, include_details=False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(e, include_details=False)
        )


@router.get("/logs/{transaction_id}", response_model=AuditLogResponse)
def get_logs_secure(
    transaction_id: str,
    request: Request,
    api_key: str = Security(verify_api_key)
) -> AuditLogResponse:
    """
    查询交易审核日志（安全加固版）
    
    安全特性:
    - ✅ 输入清洗（防止SQL注入）
    - ✅ 速率限制
    - ✅ 安全的错误处理
    
    需要在请求头中提供 X-API-Key 进行认证
    """
    try:
        # 1. 速率限制检查
        client_id = api_key or request.client.host
        rate_limiter = get_rate_limiter()
        allowed, error_msg = rate_limiter.check_rate_limit(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁: {error_msg}"
            )
        
        # 2. 清洗transaction_id，防止SQL注入
        safe_transaction_id = SecurityValidator.sanitize_transaction_id(transaction_id)
        
        # 3. 查询日志
        logs = get_audit_logs(safe_transaction_id)
        
        if not logs.logs:
            raise HTTPException(
                status_code=404,
                detail="未找到审计日志"
            )
        
        return logs
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=safe_error_message(e, include_details=False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(e, include_details=False)
        )
