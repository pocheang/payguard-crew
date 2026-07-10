"""
规则管理API
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Security, Query
from pydantic import BaseModel, Field

from app.auth.api_key import verify_api_key
from app.api.error_handler import api_error_handler
from app.services.rule_service import RuleService, RuleStatus
from app.utils.response import success_response

router = APIRouter(tags=["rules"])


class CreateRuleRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    rule_type: str = Field(..., description="规则类型：amount/frequency/location/merchant")
    weight: int = Field(default=5, ge=1, le=10, description="权重1-10")
    condition: Dict[str, Any] = Field(..., description="触发条件JSON")
    action: Dict[str, Any] = Field(..., description="执行动作JSON")


class UpdateRuleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[int] = Field(None, ge=1, le=10)
    condition: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class TestRuleRequest(BaseModel):
    test_data: Dict[str, Any] = Field(..., description="测试数据")


@router.post("/rules")
@api_error_handler
def create_rule(request: CreateRuleRequest, api_key: str = Security(verify_api_key)):
    """创建规则"""
    rule = RuleService.create_rule(
        name=request.name,
        description=request.description,
        rule_type=request.rule_type,
        weight=request.weight,
        condition=request.condition,
        action=request.action,
        created_by="api_user"  # TODO: 从token获取用户ID
    )
    return success_response(rule)


@router.get("/rules")
@api_error_handler
def list_rules(
    status: Optional[str] = Query(None),
    rule_type: Optional[str] = Query(None),
    include_archived: bool = Query(False),
    api_key: str = Security(verify_api_key)
):
    """查询规则列表"""
    rules = RuleService.list_rules(
        status=status,
        rule_type=rule_type,
        include_archived=include_archived
    )
    return {"success": True, "total": len(rules), "data": rules}


@router.get("/rules/{rule_id}")
@api_error_handler
def get_rule(rule_id: str, api_key: str = Security(verify_api_key)):
    """获取规则详情"""
    rule = RuleService.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return success_response(rule)


@router.put("/rules/{rule_id}")
@api_error_handler
def update_rule(
    rule_id: str,
    request: UpdateRuleRequest,
    api_key: str = Security(verify_api_key)
):
    """更新规则"""
    updates = request.dict(exclude_unset=True)
    rule = RuleService.update_rule(
        rule_id=rule_id,
        updates=updates,
        updated_by="api_user"
    )
    return success_response(rule)


@router.delete("/rules/{rule_id}")
@api_error_handler
def delete_rule(rule_id: str, api_key: str = Security(verify_api_key)):
    """删除规则（软删除）"""
    success = RuleService.delete_rule(rule_id, deleted_by="api_user")
    return {"success": success, "message": "Rule archived"}


@router.post("/rules/{rule_id}/activate")
@api_error_handler
def activate_rule(rule_id: str, api_key: str = Security(verify_api_key)):
    """激活规则"""
    rule = RuleService.activate_rule(rule_id, activated_by="api_user")
    return success_response(rule)


@router.post("/rules/{rule_id}/deactivate")
@api_error_handler
def deactivate_rule(rule_id: str, api_key: str = Security(verify_api_key)):
    """停用规则"""
    rule = RuleService.deactivate_rule(rule_id, deactivated_by="api_user")
    return success_response(rule)


@router.post("/rules/{rule_id}/test")
@api_error_handler
def test_rule(
    rule_id: str,
    request: TestRuleRequest,
    api_key: str = Security(verify_api_key)
):
    """测试规则"""
    result = RuleService.test_rule(rule_id, request.test_data)
    return success_response(result)


@router.post("/rules/{rule_id}/versions")
@api_error_handler
def create_rule_version(rule_id: str, api_key: str = Security(verify_api_key)):
    """创建规则版本"""
    rule = RuleService.create_rule_version(rule_id, created_by="api_user")
    return success_response(rule)


@router.get("/rules/{rule_id}/versions")
@api_error_handler
def get_rule_versions(rule_id: str, api_key: str = Security(verify_api_key)):
    """获取规则版本历史"""
    versions = RuleService.get_rule_versions(rule_id)
    return {"success": True, "total": len(versions), "data": versions}


@router.get("/rules/statistics/summary")
@api_error_handler
def get_rule_statistics(api_key: str = Security(verify_api_key)):
    """获取规则统计"""
    stats = RuleService.get_rule_statistics()
    return success_response(stats)
