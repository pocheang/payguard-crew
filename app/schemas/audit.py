from typing import Literal

from pydantic import BaseModel, Field


class TriggeredRule(BaseModel):
    rule_id: str
    rule_name: str
    reason: str
    score: int


class EvidenceItem(BaseModel):
    source: str
    content: str


class AuditResponse(BaseModel):
    transaction_id: str
    risk_level: Literal["low", "medium", "high"]
    risk_score: int
    decision: Literal["approve", "review", "hold", "reject"]
    summary: str
    triggered_rules: list[TriggeredRule]
    evidence: list[EvidenceItem]
    suggestion: str
    requires_manual_review: bool


class AuditLogEntry(BaseModel):
    agent_name: str
    input_data: str | None = None
    output_data: str | None = None
    status: str
    error_message: str | None = None
    latency_ms: int | None = None
    created_at: str | None = None


class AuditLogResponse(BaseModel):
    transaction_id: str
    logs: list[AuditLogEntry] = Field(default_factory=list)


class AuditReportRecord(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    risk_score: int
    risk_level: Literal["low", "medium", "high"]
    decision: Literal["approve", "review", "hold", "reject"]
    summary: str
    suggestion: str
    requires_manual_review: bool
    created_at: str
    triggered_rules: list[TriggeredRule] = Field(default_factory=list)
