from fastapi import APIRouter, HTTPException, Security

from app.auth.api_key import verify_api_key
from app.crew.audit_crew import run_audit_crew
from app.db.repository import get_audit_logs, get_audit_report
from app.schemas.audit import AuditLogResponse, AuditReportRecord, AuditResponse
from app.schemas.transaction import TransactionInput

router = APIRouter()


@router.post("/transaction", response_model=AuditResponse)
def audit_transaction(
    tx: TransactionInput,
    api_key: str = Security(verify_api_key)
) -> AuditResponse:
    """提交交易审核请求

    需要在请求头中提供 X-API-Key 进行认证
    """
    return run_audit_crew(tx)


@router.get("/report/{transaction_id}", response_model=AuditReportRecord)
def get_report(
    transaction_id: str,
    api_key: str = Security(verify_api_key)
) -> AuditReportRecord:
    """查询交易审核报告

    需要在请求头中提供 X-API-Key 进行认证
    """
    report = get_audit_report(transaction_id)
    if report is None:
        raise HTTPException(status_code=404, detail="audit report not found")
    return report


@router.get("/logs/{transaction_id}", response_model=AuditLogResponse)
def get_logs(
    transaction_id: str,
    api_key: str = Security(verify_api_key)
) -> AuditLogResponse:
    """查询交易审核日志

    需要在请求头中提供 X-API-Key 进行认证
    """
    logs = get_audit_logs(transaction_id)
    if not logs.logs:
        raise HTTPException(status_code=404, detail="audit logs not found")
    return logs
