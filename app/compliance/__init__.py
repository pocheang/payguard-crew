"""
合规模块初始化文件
"""
from .kyc_service import (
    KYCService,
    KYCLevel,
    KYCProfile,
    KYCVerificationRequest,
    KYCVerificationResult,
    DocumentType
)

from .aml_service import (
    AMLMonitoringService,
    AMLRiskLevel,
    SuspiciousActivityReport,
    SuspiciousActivityType,
    SARStatus,
    TransactionPattern
)

from .regulatory_reporting import (
    RegulatoryReportingService,
    RegulatoryReport,
    ReportType,
    ReportStatus
)

from .audit_trail import (
    AuditTrailService,
    AuditLog,
    AuditEventType,
    DataRetentionPolicy,
    DataRetentionRecord,
    DataAccessLog
)

__all__ = [
    # KYC
    "KYCService",
    "KYCLevel",
    "KYCProfile",
    "KYCVerificationRequest",
    "KYCVerificationResult",
    "DocumentType",

    # AML
    "AMLMonitoringService",
    "AMLRiskLevel",
    "SuspiciousActivityReport",
    "SuspiciousActivityType",
    "SARStatus",
    "TransactionPattern",

    # Regulatory Reporting
    "RegulatoryReportingService",
    "RegulatoryReport",
    "ReportType",
    "ReportStatus",

    # Audit Trail
    "AuditTrailService",
    "AuditLog",
    "AuditEventType",
    "DataRetentionPolicy",
    "DataRetentionRecord",
    "DataAccessLog"
]
