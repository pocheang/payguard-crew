"""
审核工作流API

新增接口：
1. POST /api/v1/review/create - 创建审核记录
2. POST /api/v1/review/{tx_id}/status - 更新审核状态
3. POST /api/v1/review/{tx_id}/assign - 分配审核人
4. POST /api/v1/review/{tx_id}/comment - 添加评论
5. GET /api/v1/review/{tx_id} - 获取审核详情
6. GET /api/v1/review/pending - 获取待审核列表
7. GET /api/v1/review/statistics - 获取审核统计
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Security, Query
from app.auth.api_key import verify_api_key
from app.services.review_service import (
    ReviewStatus,
    ReviewPriority,
    create_review_record,
    get_review_record,
    update_review_status,
    assign_reviewer,
    add_comment,
    get_comments,
    list_pending_reviews,
    get_review_statistics,
)

router = APIRouter(tags=["review-workflow"])


class CreateReviewRequest(BaseModel):
    """创建审核记录请求"""
    transaction_id: str = Field(..., description="交易ID")
    priority: str = Field(default="normal", description="优先级: low/normal/high/urgent")
    assigned_to: Optional[str] = Field(None, description="分配给谁")


class UpdateStatusRequest(BaseModel):
    """更新状态请求"""
    status: str = Field(..., description="新状态: pending/in_review/approved/rejected/escalated/archived")
    reviewer: str = Field(..., description="审核人")
    comment: Optional[str] = Field(None, description="备注")


class AssignRequest(BaseModel):
    """分配审核人请求"""
    assigned_to: str = Field(..., description="分配给谁")
    assigner: str = Field(..., description="分配人")


class CommentRequest(BaseModel):
    """添加评论请求"""
    user_id: str = Field(..., description="用户ID")
    comment: str = Field(..., min_length=1, max_length=2000, description="评论内容")


@router.post("/create")
def create_review(
    request: CreateReviewRequest,
    api_key: str = Security(verify_api_key)
):
    """
    创建审核记录

    适用场景：
    - 高风险交易自动创建审核单
    - 手动提交审核

    示例：
    POST /api/v1/review/create
    {
      "transaction_id": "TX001",
      "priority": "high",
      "assigned_to": "reviewer01"
    }
    """
    try:
        record = create_review_record(
            transaction_id=request.transaction_id,
            priority=request.priority,
            assigned_to=request.assigned_to
        )
        return {"success": True, "data": record}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{transaction_id}/status")
def update_status(
    transaction_id: str,
    request: UpdateStatusRequest,
    api_key: str = Security(verify_api_key)
):
    """
    更新审核状态

    状态流转规则：
    - pending -> in_review, archived
    - in_review -> approved, rejected, escalated
    - approved -> archived
    - rejected -> archived, in_review
    - escalated -> in_review, archived
    - archived -> (不可流转)

    示例：
    POST /api/v1/review/TX001/status
    {
      "status": "approved",
      "reviewer": "reviewer01",
      "comment": "验证通过，风险可控"
    }
    """
    try:
        record = update_review_status(
            transaction_id=transaction_id,
            new_status=request.status,
            reviewer=request.reviewer,
            comment=request.comment
        )
        return {"success": True, "data": record}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{transaction_id}/assign")
def assign_review(
    transaction_id: str,
    request: AssignRequest,
    api_key: str = Security(verify_api_key)
):
    """
    分配审核人

    示例：
    POST /api/v1/review/TX001/assign
    {
      "assigned_to": "reviewer02",
      "assigner": "manager01"
    }
    """
    try:
        record = assign_reviewer(
            transaction_id=transaction_id,
            assigned_to=request.assigned_to,
            assigner=request.assigner
        )
        return {"success": True, "data": record}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{transaction_id}/comment")
def add_review_comment(
    transaction_id: str,
    request: CommentRequest,
    api_key: str = Security(verify_api_key)
):
    """
    添加评论

    示例：
    POST /api/v1/review/TX001/comment
    {
      "user_id": "reviewer01",
      "comment": "需要补充KYC材料"
    }
    """
    try:
        comment = add_comment(
            transaction_id=transaction_id,
            user_id=request.user_id,
            comment=request.comment
        )
        return {"success": True, "data": comment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}")
def get_review_detail(
    transaction_id: str,
    api_key: str = Security(verify_api_key)
):
    """
    获取审核详情（包含评论历史）

    示例：
    GET /api/v1/review/TX001
    """
    try:
        record = get_review_record(transaction_id)
        if not record:
            raise HTTPException(status_code=404, detail="审核记录不存在")

        comments = get_comments(transaction_id)

        return {
            "success": True,
            "data": {
                "record": record,
                "comments": comments
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
def get_pending_reviews(
    assigned_to: Optional[str] = Query(None, description="筛选分配人"),
    priority: Optional[str] = Query(None, description="筛选优先级"),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    api_key: str = Security(verify_api_key)
):
    """
    获取待审核列表

    支持筛选：
    - 按分配人筛选
    - 按优先级筛选

    示例：
    GET /api/v1/review/pending
    GET /api/v1/review/pending?assigned_to=reviewer01
    GET /api/v1/review/pending?priority=high
    """
    try:
        reviews = list_pending_reviews(
            assigned_to=assigned_to,
            priority=priority,
            limit=limit
        )
        return {
            "success": True,
            "total": len(reviews),
            "data": reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
def get_review_stats(
    api_key: str = Security(verify_api_key)
):
    """
    获取审核统计

    返回：
    - 状态分布
    - TOP 10审核人
    - 平均审核时间

    示例：
    GET /api/v1/review/statistics
    """
    try:
        stats = get_review_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
