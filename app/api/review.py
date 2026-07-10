"""审核工作流API"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Security, Query
from app.auth.api_key import verify_api_key
from app.api.error_handler import api_error_handler
from app.services.review_service import (
    create_review_record, get_review_record, update_review_status,
    assign_reviewer, add_comment, get_comments, list_pending_reviews,
    get_review_statistics, get_overdue_reviews, check_and_escalate_overdue,
    get_review_history, validate_status_transition
)
from app.utils.response import success_response

router = APIRouter(tags=["review-workflow"])

class CreateReviewRequest(BaseModel):
    transaction_id: str = Field(..., description="交易ID")
    priority: str = Field(default="normal", description="优先级")
    assigned_to: Optional[str] = Field(None, description="分配给谁")
    auto_assign: bool = Field(default=True, description="是否自动分配")

class UpdateStatusRequest(BaseModel):
    status: str = Field(..., description="新状态")
    reviewer: str = Field(..., description="审核人")
    comment: Optional[str] = Field(None, description="备注")

class AssignRequest(BaseModel):
    assigned_to: str = Field(..., description="分配给谁")
    assigner: str = Field(..., description="分配人")

class CommentRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    comment: str = Field(..., min_length=1, max_length=2000, description="评论内容")

class ValidateTransitionRequest(BaseModel):
    current_status: str = Field(..., description="当前状态")
    new_status: str = Field(..., description="目标状态")

# 具体路径必须在 /{transaction_id} 之前
@router.post("/create")
@api_error_handler
def create_review(request: CreateReviewRequest, api_key: str = Security(verify_api_key)):
    record = create_review_record(
        request.transaction_id,
        request.priority,
        request.assigned_to,
        request.auto_assign
    )
    return success_response(record)

@router.get("/list/pending")
@api_error_handler
def get_pending_reviews_list(
    assigned_to: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=500),
    api_key: str = Security(verify_api_key)
):
    reviews = list_pending_reviews(assigned_to=assigned_to, priority=priority, limit=limit)
    return {"success": True, "total": len(reviews), "data": reviews}

@router.get("/list/overdue")
@api_error_handler
def get_overdue_reviews_list(
    timeout_hours: int = Query(default=24, ge=1, le=168),
    api_key: str = Security(verify_api_key)
):
    """获取超时审核列表"""
    reviews = get_overdue_reviews(timeout_hours)
    return {"success": True, "total": len(reviews), "data": reviews}

@router.post("/escalate/overdue")
@api_error_handler
def escalate_overdue_reviews(
    timeout_hours: int = Query(default=24, ge=1, le=168),
    escalate_to: str = Query(default="supervisor"),
    api_key: str = Security(verify_api_key)
):
    """自动升级超时审核"""
    escalated = check_and_escalate_overdue(timeout_hours, escalate_to)
    return {"success": True, "escalated_count": len(escalated), "data": escalated}

@router.post("/validate-transition")
@api_error_handler
def validate_transition(request: ValidateTransitionRequest, api_key: str = Security(verify_api_key)):
    """验证状态流转是否合法"""
    is_valid, message = validate_status_transition(request.current_status, request.new_status)
    return {"success": True, "valid": is_valid, "message": message}

@router.post("/{transaction_id}/status")
@api_error_handler
def update_status(transaction_id: str, request: UpdateStatusRequest, api_key: str = Security(verify_api_key)):
    record = update_review_status(transaction_id, request.status, request.reviewer, request.comment)
    return success_response(record)

@router.post("/{transaction_id}/assign")
@api_error_handler
def assign_review(transaction_id: str, request: AssignRequest, api_key: str = Security(verify_api_key)):
    record = assign_reviewer(transaction_id, request.assigned_to, request.assigner)
    return success_response(record)

@router.post("/{transaction_id}/comment")
@api_error_handler
def add_review_comment(transaction_id: str, request: CommentRequest, api_key: str = Security(verify_api_key)):
    comment = add_comment(transaction_id, request.user_id, request.comment)
    return success_response(comment)

@router.get("/statistics")
@api_error_handler
def get_statistics(api_key: str = Security(verify_api_key)):
    stats = get_review_statistics()
    return success_response(stats)

@router.get("/{transaction_id}/history")
@api_error_handler
def get_history(transaction_id: str, api_key: str = Security(verify_api_key)):
    """获取完整审核历史"""
    history = get_review_history(transaction_id)
    if not history:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    return success_response(history)

@router.get("/{transaction_id}")
@api_error_handler
def get_review_detail(transaction_id: str, api_key: str = Security(verify_api_key)):
    record = get_review_record(transaction_id)
    if not record:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    comments = get_comments(transaction_id)
    return {"success": True, "data": {"record": record, "comments": comments}}
