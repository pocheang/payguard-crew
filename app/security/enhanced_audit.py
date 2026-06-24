"""
增强的审计追踪服务
提供完整的操作审计、数据变更追踪和安全事件监控
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json
import hashlib
from .access_control import User, Permission
from .encryption import EncryptionService


class SecurityEventType(str, Enum):
    """安全事件类型"""
    # 认证事件
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    SESSION_EXPIRED = "session_expired"

    # 授权事件
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_ESCALATION = "permission_escalation"

    # 数据访问
    DATA_READ = "data_read"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"

    # 数据修改
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_ENCRYPTION = "data_encryption"
    DATA_DECRYPTION = "data_decryption"

    # 安全异常
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"

    # 系统事件
    CONFIG_CHANGE = "config_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"
    ENCRYPTION_KEY_ROTATION = "encryption_key_rotation"


class SeverityLevel(str, Enum):
    """严重程度"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EnhancedAuditLog(BaseModel):
    """增强的审计日志"""
    log_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # 事件信息
    event_type: SecurityEventType
    severity: SeverityLevel = SeverityLevel.INFO

    # 用户信息
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_roles: Optional[List[str]] = None

    # 请求信息
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # 操作信息
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    permission_required: Optional[str] = None

    # 数据变更
    before_value: Optional[Dict] = None
    after_value: Optional[Dict] = None
    changed_fields: Optional[List[str]] = None

    # 结果
    success: bool = True
    error_message: Optional[str] = None

    # 安全信息
    risk_score: int = 0  # 0-100
    anomaly_detected: bool = False
    anomaly_reason: Optional[str] = None

    # 数据完整性
    data_hash: Optional[str] = None
    previous_log_hash: Optional[str] = None
    chain_valid: bool = True

    # 额外元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditChain:
    """审计链 - 确保审计日志的完整性和防篡改"""

    def __init__(self):
        self.last_hash: Optional[str] = None

    def calculate_hash(self, log: EnhancedAuditLog) -> str:
        """计算审计日志的哈希值"""
        # 序列化关键数据
        data = {
            "log_id": log.log_id,
            "timestamp": log.timestamp.isoformat(),
            "event_type": log.event_type,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "previous_hash": log.previous_log_hash
        }

        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def add_to_chain(self, log: EnhancedAuditLog) -> EnhancedAuditLog:
        """将日志添加到审计链"""
        log.previous_log_hash = self.last_hash
        log.data_hash = self.calculate_hash(log)
        self.last_hash = log.data_hash
        return log

    def verify_chain(self, logs: List[EnhancedAuditLog]) -> bool:
        """验证审计链的完整性"""
        if not logs:
            return True

        for i in range(len(logs)):
            # 验证哈希
            expected_hash = self.calculate_hash(logs[i])
            if logs[i].data_hash != expected_hash:
                logs[i].chain_valid = False
                return False

            # 验证链接
            if i > 0:
                if logs[i].previous_log_hash != logs[i-1].data_hash:
                    logs[i].chain_valid = False
                    return False

        return True


class EnhancedAuditService:
    """增强的审计服务"""

    def __init__(self, db_repository, encryption_service: Optional[EncryptionService] = None):
        self.db = db_repository
        self.encryption = encryption_service
        self.audit_chain = AuditChain()

        # 异常检测阈值
        self.FAILED_LOGIN_THRESHOLD = 5
        self.RAPID_REQUEST_THRESHOLD = 20  # 每分钟
        self.SENSITIVE_ACCESS_THRESHOLD = 10  # 每小时

    async def log_security_event(
        self,
        event_type: SecurityEventType,
        user: Optional[User],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        before_value: Optional[Dict] = None,
        after_value: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> EnhancedAuditLog:
        """记录安全事件"""

        # 生成日志ID
        log_id = f"AUDIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # 确定严重程度
        severity = self._determine_severity(event_type, success)

        # 计算变更字段
        changed_fields = None
        if before_value and after_value:
            changed_fields = self._get_changed_fields(before_value, after_value)

        # 创建审计日志
        log = EnhancedAuditLog(
            log_id=log_id,
            event_type=event_type,
            severity=severity,
            user_id=user.user_id if user else None,
            username=user.username if user else None,
            user_roles=[r.value for r in user.roles] if user else None,
            ip_address=ip_address,
            request_id=request_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_value=before_value,
            after_value=after_value,
            changed_fields=changed_fields,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )

        # 异常检测
        await self._detect_anomalies(log, user)

        # 添加到审计链
        log = self.audit_chain.add_to_chain(log)

        # 如果启用了加密，加密敏感数据
        if self.encryption:
            log = await self._encrypt_sensitive_log_data(log)

        # 保存到数据库
        await self.db.save_enhanced_audit_log(log)

        # 如果是高危事件，触发告警
        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            await self._trigger_security_alert(log)

        return log

    async def log_data_access(
        self,
        user: User,
        data_type: str,
        data_id: str,
        access_type: str,
        fields_accessed: Optional[List[str]] = None,
        ip_address: Optional[str] = None,
        authorized: bool = True
    ):
        """记录数据访问"""

        event_type = SecurityEventType.DATA_READ
        if access_type == "export":
            event_type = SecurityEventType.DATA_EXPORT
        elif access_type == "delete":
            event_type = SecurityEventType.DATA_DELETE

        # 检查是否是敏感数据
        is_sensitive = await self._is_sensitive_data(data_type, fields_accessed)
        if is_sensitive:
            event_type = SecurityEventType.SENSITIVE_DATA_ACCESS

        await self.log_security_event(
            event_type=event_type,
            user=user,
            action=f"{access_type}_{data_type}",
            resource_type=data_type,
            resource_id=data_id,
            ip_address=ip_address,
            success=authorized,
            metadata={
                "access_type": access_type,
                "fields_accessed": fields_accessed,
                "is_sensitive": is_sensitive
            }
        )

    async def log_data_modification(
        self,
        user: User,
        data_type: str,
        data_id: str,
        operation: str,
        before_data: Optional[Dict],
        after_data: Optional[Dict],
        ip_address: Optional[str] = None
    ):
        """记录数据修改"""

        event_type = SecurityEventType.DATA_UPDATE
        if operation == "create":
            event_type = SecurityEventType.DATA_CREATE
        elif operation == "delete":
            event_type = SecurityEventType.DATA_DELETE

        await self.log_security_event(
            event_type=event_type,
            user=user,
            action=f"{operation}_{data_type}",
            resource_type=data_type,
            resource_id=data_id,
            before_value=before_data,
            after_value=after_data,
            ip_address=ip_address,
            metadata={"operation": operation}
        )

    async def get_user_activity(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[SecurityEventType]] = None
    ) -> List[EnhancedAuditLog]:
        """获取用户活动记录"""
        return await self.db.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            event_types=event_types
        )

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[EnhancedAuditLog]:
        """获取资源的完整历史"""
        return await self.db.get_audit_logs(
            resource_type=resource_type,
            resource_id=resource_id
        )

    async def get_security_alerts(
        self,
        severity: Optional[SeverityLevel] = None,
        start_date: Optional[datetime] = None
    ) -> List[EnhancedAuditLog]:
        """获取安全告警"""
        return await self.db.get_security_alerts(
            severity=severity,
            start_date=start_date
        )

    async def verify_audit_integrity(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """验证审计日志完整性"""

        logs = await self.db.get_audit_logs(
            start_date=start_date,
            end_date=end_date
        )

        # 重建审计链
        chain = AuditChain()
        is_valid = chain.verify_chain(logs)

        # 统计
        total_logs = len(logs)
        invalid_logs = sum(1 for log in logs if not log.chain_valid)

        return {
            "is_valid": is_valid,
            "total_logs": total_logs,
            "invalid_logs": invalid_logs,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "verification_time": datetime.utcnow().isoformat()
        }

    # 私有方法

    def _determine_severity(self, event_type: SecurityEventType, success: bool) -> SeverityLevel:
        """确定事件严重程度"""

        if event_type in [
            SecurityEventType.DATA_BREACH_ATTEMPT,
            SecurityEventType.UNAUTHORIZED_ACCESS,
            SecurityEventType.PERMISSION_ESCALATION
        ]:
            return SeverityLevel.CRITICAL

        if event_type in [
            SecurityEventType.BRUTE_FORCE_ATTEMPT,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityEventType.SENSITIVE_DATA_ACCESS
        ]:
            return SeverityLevel.HIGH

        if event_type in [
            SecurityEventType.ACCESS_DENIED,
            SecurityEventType.LOGIN_FAILED,
            SecurityEventType.DATA_DELETE
        ]:
            return SeverityLevel.MEDIUM if not success else SeverityLevel.LOW

        return SeverityLevel.INFO

    def _get_changed_fields(self, before: Dict, after: Dict) -> List[str]:
        """获取变更的字段"""
        changed = []
        all_keys = set(before.keys()) | set(after.keys())

        for key in all_keys:
            if before.get(key) != after.get(key):
                changed.append(key)

        return changed

    async def _detect_anomalies(self, log: EnhancedAuditLog, user: Optional[User]):
        """异常检测"""

        if not user:
            return

        # 检测暴力破解
        if log.event_type == SecurityEventType.LOGIN_FAILED:
            recent_failures = await self.db.count_recent_events(
                user_id=user.user_id,
                event_type=SecurityEventType.LOGIN_FAILED,
                minutes=10
            )

            if recent_failures >= self.FAILED_LOGIN_THRESHOLD:
                log.anomaly_detected = True
                log.anomaly_reason = f"连续登录失败 {recent_failures} 次"
                log.risk_score = 80
                log.event_type = SecurityEventType.BRUTE_FORCE_ATTEMPT

        # 检测快速请求
        recent_requests = await self.db.count_recent_events(
            user_id=user.user_id,
            minutes=1
        )

        if recent_requests >= self.RAPID_REQUEST_THRESHOLD:
            log.anomaly_detected = True
            log.anomaly_reason = f"请求频率异常: {recent_requests}/分钟"
            log.risk_score += 30

        # 检测敏感数据访问
        if log.event_type == SecurityEventType.SENSITIVE_DATA_ACCESS:
            recent_sensitive = await self.db.count_recent_events(
                user_id=user.user_id,
                event_type=SecurityEventType.SENSITIVE_DATA_ACCESS,
                hours=1
            )

            if recent_sensitive >= self.SENSITIVE_ACCESS_THRESHOLD:
                log.anomaly_detected = True
                log.anomaly_reason = f"敏感数据访问频繁: {recent_sensitive}/小时"
                log.risk_score += 50

    async def _is_sensitive_data(self, data_type: str, fields: Optional[List[str]]) -> bool:
        """判断是否是敏感数据"""
        sensitive_types = ["kyc_profile", "transaction", "sar", "user_credential"]
        sensitive_fields = ["id_card", "passport", "bank_account", "password", "api_key"]

        if data_type in sensitive_types:
            return True

        if fields:
            return any(f in sensitive_fields for f in fields)

        return False

    async def _encrypt_sensitive_log_data(self, log: EnhancedAuditLog) -> EnhancedAuditLog:
        """加密日志中的敏感数据"""
        # 加密 before_value 和 after_value 中的敏感字段
        # 实现略
        return log

    async def _trigger_security_alert(self, log: EnhancedAuditLog):
        """触发安全告警"""
        # TODO: 发送邮件、短信、Webhook 等告警
        print(f"🚨 安全告警: {log.event_type} - {log.anomaly_reason}")
