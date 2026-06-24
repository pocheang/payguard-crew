"""
数据留存和审计服务
确保所有关键数据按照监管要求进行保存和审计追踪
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json
import hashlib


class AuditEventType(str, Enum):
    """审计事件类型"""
    # 用户操作
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"

    # KYC 操作
    KYC_SUBMIT = "kyc_submit"
    KYC_APPROVE = "kyc_approve"
    KYC_REJECT = "kyc_reject"
    KYC_UPDATE = "kyc_update"

    # 交易操作
    TRANSACTION_CREATE = "transaction_create"
    TRANSACTION_APPROVE = "transaction_approve"
    TRANSACTION_REJECT = "transaction_reject"
    TRANSACTION_CANCEL = "transaction_cancel"

    # AML 操作
    SAR_CREATE = "sar_create"
    SAR_UPDATE = "sar_update"
    SAR_FILE = "sar_file"

    # 系统操作
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    RISK_RULE_UPDATE = "risk_rule_update"
    REPORT_GENERATE = "report_generate"
    DATA_EXPORT = "data_export"


class DataRetentionPolicy(str, Enum):
    """数据留存策略"""
    SHORT_TERM = "short_term"  # 3个月
    MEDIUM_TERM = "medium_term"  # 1年
    LONG_TERM = "long_term"  # 5年
    PERMANENT = "permanent"  # 永久保存


class AuditLog(BaseModel):
    """审计日志"""
    log_id: str
    event_type: AuditEventType

    # 操作信息
    user_id: Optional[str] = None
    operator_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # 事件详情
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str

    # 数据
    before_data: Optional[Dict] = None
    after_data: Optional[Dict] = None
    changes: Optional[Dict] = None

    # 结果
    success: bool = True
    error_message: Optional[str] = None

    # 元数据
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # 数据完整性
    checksum: Optional[str] = None


class DataRetentionRecord(BaseModel):
    """数据留存记录"""
    record_id: str
    data_type: str  # transaction, kyc_profile, sar, audit_log
    data_id: str

    # 留存策略
    retention_policy: DataRetentionPolicy
    retention_period_days: int

    # 数据快照
    data_snapshot: Dict
    data_hash: str

    # 状态
    archived: bool = False
    archived_at: Optional[datetime] = None
    archive_location: Optional[str] = None

    # 访问控制
    can_be_deleted: bool = False
    deletion_date: Optional[datetime] = None

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class DataAccessLog(BaseModel):
    """数据访问日志"""
    access_id: str
    user_id: str

    # 访问信息
    data_type: str
    data_id: str
    access_type: str  # read, export, delete

    # 请求信息
    ip_address: str
    user_agent: Optional[str] = None

    # 授权信息
    authorized: bool
    authorization_reason: Optional[str] = None

    # 结果
    success: bool
    accessed_fields: Optional[List[str]] = None

    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditTrailService:
    """审计追踪服务"""

    def __init__(self, db_repository):
        self.db = db_repository

        # 留存期限配置（天数）
        self.RETENTION_PERIODS = {
            DataRetentionPolicy.SHORT_TERM: 90,
            DataRetentionPolicy.MEDIUM_TERM: 365,
            DataRetentionPolicy.LONG_TERM: 1825,  # 5年
            DataRetentionPolicy.PERMANENT: -1  # 永久
        }

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        operator_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        before_data: Optional[Dict] = None,
        after_data: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """记录审计事件"""

        # 计算数据变更
        changes = None
        if before_data and after_data:
            changes = self._calculate_changes(before_data, after_data)

        # 生成日志ID
        log_id = f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # 创建审计日志
        audit_log = AuditLog(
            log_id=log_id,
            event_type=event_type,
            user_id=user_id,
            operator_id=operator_id,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            before_data=before_data,
            after_data=after_data,
            changes=changes,
            success=success,
            error_message=error_message,
            request_id=request_id
        )

        # 计算校验和
        audit_log.checksum = self._calculate_checksum(audit_log)

        # 保存到数据库
        await self.db.save_audit_log(audit_log)

        # 如果是关键操作，同时创建留存记录
        if self._is_critical_event(event_type):
            await self.create_retention_record(
                data_type="audit_log",
                data_id=log_id,
                data_snapshot=audit_log.dict(),
                retention_policy=DataRetentionPolicy.LONG_TERM
            )

        return audit_log

    async def create_retention_record(
        self,
        data_type: str,
        data_id: str,
        data_snapshot: Dict,
        retention_policy: DataRetentionPolicy
    ) -> DataRetentionRecord:
        """创建数据留存记录"""

        # 计算留存期限
        retention_days = self.RETENTION_PERIODS[retention_policy]
        expires_at = None
        if retention_days > 0:
            expires_at = datetime.utcnow() + timedelta(days=retention_days)

        # 计算数据哈希
        data_hash = self._calculate_data_hash(data_snapshot)

        # 生成记录ID
        record_id = f"RET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{data_type}-{data_id}"

        record = DataRetentionRecord(
            record_id=record_id,
            data_type=data_type,
            data_id=data_id,
            retention_policy=retention_policy,
            retention_period_days=retention_days,
            data_snapshot=data_snapshot,
            data_hash=data_hash,
            expires_at=expires_at,
            can_be_deleted=(retention_policy != DataRetentionPolicy.PERMANENT)
        )

        await self.db.save_retention_record(record)
        return record

    async def log_data_access(
        self,
        user_id: str,
        data_type: str,
        data_id: str,
        access_type: str,
        ip_address: str,
        authorized: bool,
        success: bool,
        accessed_fields: Optional[List[str]] = None,
        authorization_reason: Optional[str] = None
    ) -> DataAccessLog:
        """记录数据访问日志"""

        access_id = f"ACC-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        access_log = DataAccessLog(
            access_id=access_id,
            user_id=user_id,
            data_type=data_type,
            data_id=data_id,
            access_type=access_type,
            ip_address=ip_address,
            authorized=authorized,
            authorization_reason=authorization_reason,
            success=success,
            accessed_fields=accessed_fields
        )

        await self.db.save_access_log(access_log)
        return access_log

    async def get_audit_trail(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """获取审计追踪"""

        return await self.db.get_audit_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

    async def verify_audit_log_integrity(self, log_id: str) -> bool:
        """验证审计日志完整性"""

        log = await self.db.get_audit_log(log_id)
        if not log:
            return False

        # 重新计算校验和
        stored_checksum = log.checksum
        log.checksum = None
        calculated_checksum = self._calculate_checksum(log)

        return stored_checksum == calculated_checksum

    async def archive_expired_data(self) -> Dict[str, int]:
        """归档过期数据"""

        # 获取需要归档的记录
        expired_records = await self.db.get_expired_retention_records()

        archived_count = 0
        for record in expired_records:
            # 归档到冷存储
            archive_location = await self._archive_to_cold_storage(record)

            record.archived = True
            record.archived_at = datetime.utcnow()
            record.archive_location = archive_location

            await self.db.update_retention_record(record)
            archived_count += 1

        return {
            "archived_count": archived_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "summary"
    ) -> Dict:
        """生成审计报告"""

        logs = await self.get_audit_trail(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )

        # 统计分析
        event_distribution = {}
        user_activity = {}
        hourly_distribution = [0] * 24

        for log in logs:
            # 事件类型分布
            event_type = log.event_type
            event_distribution[event_type] = event_distribution.get(event_type, 0) + 1

            # 用户活动统计
            if log.user_id:
                user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1

            # 小时分布
            hour = log.timestamp.hour
            hourly_distribution[hour] += 1

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_events": len(logs),
            "event_distribution": event_distribution,
            "top_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
            "hourly_distribution": hourly_distribution,
            "failed_operations": sum(1 for log in logs if not log.success)
        }

    # 私有方法

    def _calculate_changes(self, before: Dict, after: Dict) -> Dict:
        """计算数据变更"""
        changes = {}

        all_keys = set(before.keys()) | set(after.keys())

        for key in all_keys:
            before_value = before.get(key)
            after_value = after.get(key)

            if before_value != after_value:
                changes[key] = {
                    "before": before_value,
                    "after": after_value
                }

        return changes

    def _calculate_checksum(self, audit_log: AuditLog) -> str:
        """计算审计日志校验和"""
        # 序列化关键字段
        data = {
            "log_id": audit_log.log_id,
            "event_type": audit_log.event_type,
            "timestamp": audit_log.timestamp.isoformat(),
            "action": audit_log.action,
            "user_id": audit_log.user_id,
            "resource_id": audit_log.resource_id
        }

        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _calculate_data_hash(self, data: Dict) -> str:
        """计算数据哈希"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _is_critical_event(self, event_type: AuditEventType) -> bool:
        """判断是否为关键事件"""
        critical_events = [
            AuditEventType.KYC_APPROVE,
            AuditEventType.KYC_REJECT,
            AuditEventType.TRANSACTION_REJECT,
            AuditEventType.SAR_FILE,
            AuditEventType.SYSTEM_CONFIG_CHANGE,
            AuditEventType.RISK_RULE_UPDATE
        ]
        return event_type in critical_events

    async def _archive_to_cold_storage(self, record: DataRetentionRecord) -> str:
        """归档到冷存储"""
        # TODO: 实际归档到云存储或归档系统
        archive_path = f"archives/{record.data_type}/{record.record_id}.json"
        return archive_path
