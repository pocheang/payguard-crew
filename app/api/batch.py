"""
批量审计和导出API

新增接口：
1. POST /api/v1/audit/batch - 批量审计交易
2. GET /api/v1/audit/export/csv - 导出CSV报告
3. GET /api/v1/audit/export/excel - 导出Excel报告
4. GET /api/v1/audit/statistics - 获取统计信息
"""
import asyncio
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Security, Query, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.auth.api_key import verify_api_key
from app.schemas.transaction import TransactionInput
from app.schemas.audit import AuditResponse
from app.services.batch_service import (
    batch_audit_transactions,
    export_audit_reports_csv,
    export_audit_reports_excel,
    get_audit_statistics,
)

router = APIRouter(tags=["batch-audit"])


class BatchAuditRequest(BaseModel):
    """批量审计请求"""
    transactions: List[TransactionInput] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="交易列表（最多100个）"
    )
    max_concurrent: int = Field(
        default=10,
        ge=1,
        le=50,
        description="最大并发数（1-50）"
    )


class BatchAuditResponse(BaseModel):
    """批量审计响应"""
    total: int = Field(..., description="总数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    results: List[AuditResponse] = Field(..., description="审计结果列表")
    duration_seconds: float = Field(..., description="耗时（秒）")


@router.post("/batch", response_model=BatchAuditResponse)
async def batch_audit(
    request: BatchAuditRequest,
    api_key: str = Security(verify_api_key)
):
    """
    批量审计交易

    性能参考：
    - 10个交易: ~3-5秒
    - 50个交易: ~15-25秒
    - 100个交易: ~30-50秒

    限制：
    - 单次最多100个交易
    - 最大并发50
    """
    import time
    start_time = time.time()

    total = len(request.transactions)

    # 执行批量审计
    results = await batch_audit_transactions(
        request.transactions,
        max_concurrent=request.max_concurrent
    )

    success = len(results)
    failed = total - success
    duration = time.time() - start_time

    return BatchAuditResponse(
        total=total,
        success=success,
        failed=failed,
        results=results,
        duration_seconds=round(duration, 2)
    )


@router.get("/export/csv")
def export_csv(
    transaction_ids: List[str] = Query(..., description="交易ID列表"),
    api_key: str = Security(verify_api_key)
):
    """
    导出审计报告为CSV

    示例：
    GET /api/v1/audit/export/csv?transaction_ids=TX001&transaction_ids=TX002

    返回：CSV文件下载
    """
    if not transaction_ids:
        raise HTTPException(status_code=400, detail="至少提供一个交易ID")

    if len(transaction_ids) > 1000:
        raise HTTPException(status_code=400, detail="单次最多导出1000条记录")

    try:
        # 生成临时文件
        import tempfile
        import os
        fd, temp_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)

        # 导出
        output_path = export_audit_reports_csv(transaction_ids, temp_path)

        # 返回文件
        return FileResponse(
            path=output_path,
            filename=f"audit_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/export/excel")
def export_excel(
    transaction_ids: List[str] = Query(..., description="交易ID列表"),
    api_key: str = Security(verify_api_key)
):
    """
    导出审计报告为Excel（带格式）

    示例：
    GET /api/v1/audit/export/excel?transaction_ids=TX001&transaction_ids=TX002

    返回：Excel文件下载

    注意：需要安装 openpyxl
    pip install openpyxl
    """
    if not transaction_ids:
        raise HTTPException(status_code=400, detail="至少提供一个交易ID")

    if len(transaction_ids) > 1000:
        raise HTTPException(status_code=400, detail="单次最多导出1000条记录")

    try:
        # 生成临时文件
        import tempfile
        import os
        fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)

        # 导出
        output_path = export_audit_reports_excel(transaction_ids, temp_path)

        # 返回文件
        return FileResponse(
            path=output_path,
            filename=f"audit_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Excel导出需要安装 openpyxl: pip install openpyxl"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/statistics")
def get_statistics(
    start_date: str = Query(None, description="开始日期 (ISO格式: 2026-01-01)"),
    end_date: str = Query(None, description="结束日期 (ISO格式: 2026-12-31)"),
    api_key: str = Security(verify_api_key)
):
    """
    获取审计统计信息

    返回：
    - 总交易数
    - 风险等级分布
    - 决策分布
    - 平均风险分数
    - 人工审核率
    - 最常触发的规则 (TOP 10)

    示例：
    GET /api/v1/audit/statistics
    GET /api/v1/audit/statistics?start_date=2026-01-01&end_date=2026-12-31
    """
    try:
        stats = get_audit_statistics(start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")


@router.get("/list")
def list_audit_reports(
    limit: int = Query(default=100, ge=1, le=1000, description="返回数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    risk_level: str = Query(None, description="风险等级筛选: low/medium/high"),
    decision: str = Query(None, description="决策筛选: approve/review/reject"),
    api_key: str = Security(verify_api_key)
):
    """
    查询审计报告列表

    支持分页和筛选

    示例：
    GET /api/v1/audit/list?limit=50&offset=0
    GET /api/v1/audit/list?risk_level=high&decision=reject
    """
    from app.db.database import get_connection

    try:
        with get_connection() as conn:
            # 构建查询
            query = "SELECT * FROM audit_reports WHERE 1=1"
            params = []

            if risk_level:
                query += " AND risk_level = ?"
                params.append(risk_level)

            if decision:
                query += " AND decision = ?"
                params.append(decision)

            # 排序和分页
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) as count FROM audit_reports WHERE 1=1"
            count_params = []
            if risk_level:
                count_query += " AND risk_level = ?"
                count_params.append(risk_level)
            if decision:
                count_query += " AND decision = ?"
                count_params.append(decision)

            total = conn.execute(count_query, count_params).fetchone()['count']

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "items": [dict(row) for row in rows]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
