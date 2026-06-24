"""
AML (Anti-Money Laundering) 反洗钱监控服务
包括交易监控、可疑活动检测、案例管理等
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AMLRiskLevel(str, Enum):
    """AML 风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuspiciousActivityType(str, Enum):
    """可疑活动类型"""
    STRUCTURING = "structuring"  # 拆分交易
    RAPID_MOVEMENT = "rapid_movement"  # 快速转移资金
    HIGH_VOLUME = "high_volume"  # 高额交易
    UNUSUAL_PATTERN = "unusual_pattern"  # 异常模式
    ROUND_AMOUNT = "round_amount"  # 整数交易
    MULTIPLE_ACCOUNTS = "multiple_accounts"  # 多账户操作
    HIGH_RISK_COUNTRY = "high_risk_country"  # 高风险国家/地区
    PEP_RELATED = "pep_related"  # 政治敏感人物


class SARStatus(str, Enum):
    """SAR (Suspicious Activity Report) 状态"""
    DETECTED = "detected"  # 已检测
    UNDER_REVIEW = "under_review"  # 审核中
    CONFIRMED = "confirmed"  # 已确认
    FILED = "filed"  # 已报告
    DISMISSED = "dismissed"  # 已驳回


class SuspiciousActivityReport(BaseModel):
    """可疑活动报告 (SAR)"""
    sar_id: str
    user_id: str
    activity_type: SuspiciousActivityType
    risk_level: AMLRiskLevel

    # 交易信息
    related_transactions: List[str] = Field(default_factory=list)
    total_amount: float = 0.0
    currency: str = "CNY"

    # 检测信息
    detection_date: datetime = Field(default_factory=datetime.utcnow)
    detection_rules: List[str] = Field(default_factory=list)
    detection_score: float = 0.0

    # 描述
    description: str
    detailed_findings: Optional[str] = None

    # 状态和审核
    status: SARStatus = SARStatus.DETECTED
    assigned_to: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None

    # 报告
    filed_to_authority: bool = False
    filing_date: Optional[datetime] = None
    filing_reference: Optional[str] = None

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TransactionPattern(BaseModel):
    """交易模式分析"""
    user_id: str
    time_period_days: int = 30

    # 统计数据
    total_transactions: int = 0
    total_amount: float = 0.0
    avg_transaction_amount: float = 0.0
    max_transaction_amount: float = 0.0

    # 模式指标
    transaction_frequency: float = 0.0  # 每天交易次数
    amount_variance: float = 0.0  # 金额方差
    time_pattern_score: float = 0.0  # 时间模式异常分数

    # 风险标记
    has_structuring_pattern: bool = False
    has_rapid_movement: bool = False
    has_round_amounts: bool = False

    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class AMLMonitoringService:
    """AML 监控服务"""

    def __init__(self, db_repository):
        self.db = db_repository

        # 阈值配置
        self.STRUCTURING_THRESHOLD = 9000  # 拆分交易阈值
        self.HIGH_VOLUME_THRESHOLD = 50000  # 高额交易阈值
        self.DAILY_TRANSACTION_LIMIT = 10  # 每日交易次数限制
        self.RAPID_MOVEMENT_HOURS = 24  # 快速转移时间窗口

    async def monitor_transaction(self, transaction_data: Dict) -> Optional[SuspiciousActivityReport]:
        """监控单笔交易"""
        user_id = transaction_data.get("user_id")
        amount = transaction_data.get("amount")

        suspicious_indicators = []
        risk_score = 0.0

        # 1. 检测拆分交易（Structuring）
        if self._detect_structuring(user_id, amount):
            suspicious_indicators.append("structuring")
            risk_score += 30

        # 2. 检测高额交易
        if amount > self.HIGH_VOLUME_THRESHOLD:
            suspicious_indicators.append("high_volume")
            risk_score += 20

        # 3. 检测整数交易
        if self._is_round_amount(amount):
            suspicious_indicators.append("round_amount")
            risk_score += 10

        # 4. 检测快速资金转移
        if await self._detect_rapid_movement(user_id):
            suspicious_indicators.append("rapid_movement")
            risk_score += 25

        # 5. 检测异常交易模式
        pattern_score = await self._analyze_transaction_pattern(user_id)
        if pattern_score > 0.7:
            suspicious_indicators.append("unusual_pattern")
            risk_score += pattern_score * 20

        # 如果有可疑指标，创建 SAR
        if suspicious_indicators:
            return await self._create_sar(
                user_id=user_id,
                transaction_data=transaction_data,
                indicators=suspicious_indicators,
                risk_score=risk_score
            )

        return None

    async def analyze_user_activity(self, user_id: str, days: int = 30) -> TransactionPattern:
        """分析用户交易活动"""
        # 获取用户近期交易
        transactions = await self.db.get_user_transactions(user_id, days)

        if not transactions:
            return TransactionPattern(user_id=user_id, time_period_days=days)

        # 计算统计数据
        total_count = len(transactions)
        amounts = [t.get("amount", 0) for t in transactions]
        total_amount = sum(amounts)
        avg_amount = total_amount / total_count if total_count > 0 else 0
        max_amount = max(amounts) if amounts else 0

        # 计算交易频率
        frequency = total_count / days

        # 计算金额方差
        variance = self._calculate_variance(amounts, avg_amount)

        # 检测模式
        has_structuring = self._check_structuring_pattern(amounts)
        has_rapid = self._check_rapid_pattern(transactions)
        has_rounds = sum(1 for a in amounts if self._is_round_amount(a)) / total_count > 0.5

        return TransactionPattern(
            user_id=user_id,
            time_period_days=days,
            total_transactions=total_count,
            total_amount=total_amount,
            avg_transaction_amount=avg_amount,
            max_transaction_amount=max_amount,
            transaction_frequency=frequency,
            amount_variance=variance,
            has_structuring_pattern=has_structuring,
            has_rapid_movement=has_rapid,
            has_round_amounts=has_rounds
        )

    async def get_all_sars(
        self,
        status: Optional[SARStatus] = None,
        risk_level: Optional[AMLRiskLevel] = None,
        days: int = 30
    ) -> List[SuspiciousActivityReport]:
        """获取所有 SAR 报告"""
        return await self.db.get_sars(status=status, risk_level=risk_level, days=days)

    async def update_sar_status(
        self,
        sar_id: str,
        new_status: SARStatus,
        reviewer: str,
        notes: Optional[str] = None
    ) -> SuspiciousActivityReport:
        """更新 SAR 状态"""
        sar = await self.db.get_sar(sar_id)
        sar.status = new_status
        sar.reviewed_by = reviewer
        sar.review_notes = notes
        sar.updated_at = datetime.utcnow()

        await self.db.update_sar(sar)
        return sar

    async def file_sar_to_authority(
        self,
        sar_id: str,
        filing_reference: str
    ) -> SuspiciousActivityReport:
        """向监管机构报告 SAR"""
        sar = await self.db.get_sar(sar_id)
        sar.filed_to_authority = True
        sar.filing_date = datetime.utcnow()
        sar.filing_reference = filing_reference
        sar.status = SARStatus.FILED
        sar.updated_at = datetime.utcnow()

        await self.db.update_sar(sar)

        # TODO: 实际向监管机构提交报告
        await self._submit_to_regulator(sar)

        return sar

    # 私有方法

    def _detect_structuring(self, user_id: str, amount: float) -> bool:
        """检测拆分交易"""
        # 检查是否接近报告阈值但低于阈值
        return 0.8 * self.STRUCTURING_THRESHOLD <= amount < self.STRUCTURING_THRESHOLD

    async def _detect_rapid_movement(self, user_id: str) -> bool:
        """检测快速资金转移"""
        recent_transactions = await self.db.get_user_transactions(
            user_id,
            hours=self.RAPID_MOVEMENT_HOURS
        )
        # 检查短时间内多笔交易
        return len(recent_transactions) > 5

    def _is_round_amount(self, amount: float) -> bool:
        """检测整数金额"""
        return amount % 1000 == 0 and amount >= 1000

    async def _analyze_transaction_pattern(self, user_id: str) -> float:
        """分析交易模式异常分数"""
        pattern = await self.analyze_user_activity(user_id)

        score = 0.0

        # 高频交易
        if pattern.transaction_frequency > 5:
            score += 0.3

        # 高金额方差
        if pattern.amount_variance > pattern.avg_transaction_amount * 2:
            score += 0.2

        # 有拆分模式
        if pattern.has_structuring_pattern:
            score += 0.3

        # 快速转移
        if pattern.has_rapid_movement:
            score += 0.2

        return min(score, 1.0)

    def _calculate_variance(self, amounts: List[float], avg: float) -> float:
        """计算方差"""
        if not amounts:
            return 0.0
        return sum((x - avg) ** 2 for x in amounts) / len(amounts)

    def _check_structuring_pattern(self, amounts: List[float]) -> bool:
        """检查是否有拆分交易模式"""
        # 检查是否有多笔接近阈值的交易
        near_threshold = [a for a in amounts if 0.8 * self.STRUCTURING_THRESHOLD <= a < self.STRUCTURING_THRESHOLD]
        return len(near_threshold) >= 3

    def _check_rapid_pattern(self, transactions: List[Dict]) -> bool:
        """检查是否有快速转移模式"""
        if len(transactions) < 2:
            return False

        # 检查连续交易的时间间隔
        timestamps = sorted([t.get("timestamp") for t in transactions])
        for i in range(len(timestamps) - 1):
            if (timestamps[i + 1] - timestamps[i]).total_seconds() < 3600:  # 1小时内
                return True

        return False

    async def _create_sar(
        self,
        user_id: str,
        transaction_data: Dict,
        indicators: List[str],
        risk_score: float
    ) -> SuspiciousActivityReport:
        """创建可疑活动报告"""
        # 确定风险等级
        if risk_score >= 70:
            risk_level = AMLRiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = AMLRiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = AMLRiskLevel.MEDIUM
        else:
            risk_level = AMLRiskLevel.LOW

        # 确定活动类型
        if "structuring" in indicators:
            activity_type = SuspiciousActivityType.STRUCTURING
        elif "rapid_movement" in indicators:
            activity_type = SuspiciousActivityType.RAPID_MOVEMENT
        elif "high_volume" in indicators:
            activity_type = SuspiciousActivityType.HIGH_VOLUME
        else:
            activity_type = SuspiciousActivityType.UNUSUAL_PATTERN

        sar = SuspiciousActivityReport(
            sar_id=f"SAR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id}",
            user_id=user_id,
            activity_type=activity_type,
            risk_level=risk_level,
            related_transactions=[transaction_data.get("transaction_id")],
            total_amount=transaction_data.get("amount", 0),
            detection_rules=indicators,
            detection_score=risk_score,
            description=f"检测到可疑活动: {', '.join(indicators)}"
        )

        await self.db.save_sar(sar)
        return sar

    async def _submit_to_regulator(self, sar: SuspiciousActivityReport):
        """向监管机构提交报告"""
        # TODO: 实际API调用
        pass
