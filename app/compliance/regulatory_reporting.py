"""
监管报告服务
生成各类合规报告供监管机构审查
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """报告类型"""
    DAILY_TRANSACTION = "daily_transaction"  # 每日交易报告
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # 可疑活动报告
    KYC_SUMMARY = "kyc_summary"  # KYC 汇总报告
    HIGH_RISK_USERS = "high_risk_users"  # 高风险用户报告
    LARGE_TRANSACTION = "large_transaction"  # 大额交易报告
    CROSS_BORDER = "cross_border"  # 跨境交易报告
    QUARTERLY_COMPLIANCE = "quarterly_compliance"  # 季度合规报告
    ANNUAL_AUDIT = "annual_audit"  # 年度审计报告


class ReportStatus(str, Enum):
    """报告状态"""
    GENERATING = "generating"
    READY = "ready"
    SUBMITTED = "submitted"
    ARCHIVED = "archived"


class RegulatoryReport(BaseModel):
    """监管报告"""
    report_id: str
    report_type: ReportType
    report_period_start: datetime
    report_period_end: datetime

    # 报告内容
    summary: Dict = Field(default_factory=dict)
    detailed_data: Dict = Field(default_factory=dict)
    statistics: Dict = Field(default_factory=dict)

    # 状态
    status: ReportStatus = ReportStatus.GENERATING
    generated_at: Optional[datetime] = None
    generated_by: str

    # 提交信息
    submitted_to: Optional[str] = None
    submitted_at: Optional[datetime] = None
    submission_reference: Optional[str] = None

    # 文件
    file_path: Optional[str] = None
    file_format: str = "PDF"  # PDF, CSV, JSON

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RegulatoryReportingService:
    """监管报告服务"""

    def __init__(self, db_repository, kyc_service, aml_service):
        self.db = db_repository
        self.kyc = kyc_service
        self.aml = aml_service

    async def generate_daily_transaction_report(
        self,
        date: datetime,
        generated_by: str
    ) -> RegulatoryReport:
        """生成每日交易报告"""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        # 获取当日交易数据
        transactions = await self.db.get_transactions_by_period(start, end)

        # 统计数据
        total_count = len(transactions)
        total_amount = sum(t.get("amount", 0) for t in transactions)
        avg_amount = total_amount / total_count if total_count > 0 else 0

        # 按风险等级分类
        risk_distribution = {
            "low": sum(1 for t in transactions if t.get("risk_level") == "low"),
            "medium": sum(1 for t in transactions if t.get("risk_level") == "medium"),
            "high": sum(1 for t in transactions if t.get("risk_level") == "high")
        }

        # 被拒绝的交易
        rejected_count = sum(1 for t in transactions if t.get("decision") == "reject")

        report = RegulatoryReport(
            report_id=f"DTR-{date.strftime('%Y%m%d')}",
            report_type=ReportType.DAILY_TRANSACTION,
            report_period_start=start,
            report_period_end=end,
            generated_by=generated_by,
            summary={
                "total_transactions": total_count,
                "total_amount": total_amount,
                "average_amount": avg_amount,
                "rejected_transactions": rejected_count
            },
            statistics={
                "risk_distribution": risk_distribution,
                "currencies": self._get_currency_distribution(transactions),
                "merchant_distribution": self._get_merchant_distribution(transactions)
            },
            detailed_data={
                "high_risk_transactions": [
                    t for t in transactions if t.get("risk_level") == "high"
                ][:100]  # 限制前100条
            }
        )

        report.status = ReportStatus.READY
        report.generated_at = datetime.utcnow()

        # 生成PDF文件
        file_path = await self._generate_pdf(report)
        report.file_path = file_path

        await self.db.save_report(report)
        return report

    async def generate_suspicious_activity_report(
        self,
        period_days: int,
        generated_by: str
    ) -> RegulatoryReport:
        """生成可疑活动报告"""
        end = datetime.utcnow()
        start = end - timedelta(days=period_days)

        # 获取所有 SAR
        sars = await self.aml.get_all_sars(days=period_days)

        # 按风险等级分类
        risk_distribution = {
            "low": sum(1 for s in sars if s.risk_level == "low"),
            "medium": sum(1 for s in sars if s.risk_level == "medium"),
            "high": sum(1 for s in sars if s.risk_level == "high"),
            "critical": sum(1 for s in sars if s.risk_level == "critical")
        }

        # 按活动类型分类
        activity_distribution = {}
        for sar in sars:
            activity_type = sar.activity_type
            activity_distribution[activity_type] = activity_distribution.get(activity_type, 0) + 1

        # 已报告数量
        filed_count = sum(1 for s in sars if s.filed_to_authority)

        report = RegulatoryReport(
            report_id=f"SAR-{end.strftime('%Y%m%d')}",
            report_type=ReportType.SUSPICIOUS_ACTIVITY,
            report_period_start=start,
            report_period_end=end,
            generated_by=generated_by,
            summary={
                "total_sars": len(sars),
                "filed_to_authority": filed_count,
                "pending_review": sum(1 for s in sars if s.status == "under_review")
            },
            statistics={
                "risk_distribution": risk_distribution,
                "activity_distribution": activity_distribution,
                "status_distribution": self._get_sar_status_distribution(sars)
            },
            detailed_data={
                "high_risk_sars": [
                    self._serialize_sar(s) for s in sars
                    if s.risk_level in ["high", "critical"]
                ]
            }
        )

        report.status = ReportStatus.READY
        report.generated_at = datetime.utcnow()

        file_path = await self._generate_pdf(report)
        report.file_path = file_path

        await self.db.save_report(report)
        return report

    async def generate_kyc_summary_report(
        self,
        period_days: int,
        generated_by: str
    ) -> RegulatoryReport:
        """生成 KYC 汇总报告"""
        end = datetime.utcnow()
        start = end - timedelta(days=period_days)

        # 获取所有 KYC 档案
        all_profiles = await self.db.get_all_kyc_profiles()

        # 按 KYC 等级分类
        level_distribution = {}
        for profile in all_profiles:
            level = profile.kyc_level
            level_distribution[level] = level_distribution.get(level, 0) + 1

        # 新注册用户的 KYC 完成率
        new_profiles = [
            p for p in all_profiles
            if start <= p.created_at <= end
        ]

        report = RegulatoryReport(
            report_id=f"KYC-{end.strftime('%Y%m%d')}",
            report_type=ReportType.KYC_SUMMARY,
            report_period_start=start,
            report_period_end=end,
            generated_by=generated_by,
            summary={
                "total_users": len(all_profiles),
                "new_users": len(new_profiles),
                "fully_verified": level_distribution.get("full_verified", 0),
                "verification_rate": level_distribution.get("full_verified", 0) / len(all_profiles) if all_profiles else 0
            },
            statistics={
                "level_distribution": level_distribution,
                "verification_methods": {
                    "phone_verified": sum(1 for p in all_profiles if p.phone_verified),
                    "email_verified": sum(1 for p in all_profiles if p.email_verified),
                    "face_verified": sum(1 for p in all_profiles if p.face_verified),
                    "address_verified": sum(1 for p in all_profiles if p.address_verified)
                }
            }
        )

        report.status = ReportStatus.READY
        report.generated_at = datetime.utcnow()

        file_path = await self._generate_pdf(report)
        report.file_path = file_path

        await self.db.save_report(report)
        return report

    async def generate_large_transaction_report(
        self,
        threshold: float,
        period_days: int,
        generated_by: str
    ) -> RegulatoryReport:
        """生成大额交易报告"""
        end = datetime.utcnow()
        start = end - timedelta(days=period_days)

        # 获取大额交易
        transactions = await self.db.get_transactions_by_period(start, end)
        large_transactions = [t for t in transactions if t.get("amount", 0) >= threshold]

        report = RegulatoryReport(
            report_id=f"LTR-{end.strftime('%Y%m%d')}",
            report_type=ReportType.LARGE_TRANSACTION,
            report_period_start=start,
            report_period_end=end,
            generated_by=generated_by,
            summary={
                "total_large_transactions": len(large_transactions),
                "total_amount": sum(t.get("amount", 0) for t in large_transactions),
                "threshold": threshold
            },
            detailed_data={
                "transactions": large_transactions
            }
        )

        report.status = ReportStatus.READY
        report.generated_at = datetime.utcnow()

        file_path = await self._generate_pdf(report)
        report.file_path = file_path

        await self.db.save_report(report)
        return report

    async def submit_report_to_regulator(
        self,
        report_id: str,
        regulator_name: str,
        submission_method: str = "API"
    ) -> RegulatoryReport:
        """向监管机构提交报告"""
        report = await self.db.get_report(report_id)

        # 生成提交参考号
        submission_ref = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # TODO: 实际提交到监管机构
        await self._submit_to_regulator_api(report, regulator_name, submission_method)

        report.status = ReportStatus.SUBMITTED
        report.submitted_to = regulator_name
        report.submitted_at = datetime.utcnow()
        report.submission_reference = submission_ref
        report.updated_at = datetime.utcnow()

        await self.db.update_report(report)
        return report

    # 私有方法

    def _get_currency_distribution(self, transactions: List[Dict]) -> Dict:
        """获取货币分布"""
        distribution = {}
        for t in transactions:
            currency = t.get("currency", "CNY")
            distribution[currency] = distribution.get(currency, 0) + 1
        return distribution

    def _get_merchant_distribution(self, transactions: List[Dict]) -> Dict:
        """获取商户分布"""
        distribution = {}
        for t in transactions:
            merchant = t.get("merchant_id", "unknown")
            distribution[merchant] = distribution.get(merchant, 0) + 1
        # 返回前10名
        sorted_merchants = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:10]
        return dict(sorted_merchants)

    def _get_sar_status_distribution(self, sars: List) -> Dict:
        """获取 SAR 状态分布"""
        distribution = {}
        for sar in sars:
            status = sar.status
            distribution[status] = distribution.get(status, 0) + 1
        return distribution

    def _serialize_sar(self, sar) -> Dict:
        """序列化 SAR 对象"""
        return {
            "sar_id": sar.sar_id,
            "user_id": sar.user_id,
            "activity_type": sar.activity_type,
            "risk_level": sar.risk_level,
            "total_amount": sar.total_amount,
            "status": sar.status,
            "detection_date": sar.detection_date.isoformat()
        }

    async def _generate_pdf(self, report: RegulatoryReport) -> str:
        """生成 PDF 报告"""
        # TODO: 实际 PDF 生成逻辑
        filename = f"{report.report_id}.pdf"
        file_path = f"reports/{filename}"
        return file_path

    async def _submit_to_regulator_api(
        self,
        report: RegulatoryReport,
        regulator_name: str,
        method: str
    ):
        """通过 API 提交到监管机构"""
        # TODO: 实际 API 调用
        # 空实现