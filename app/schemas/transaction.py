"""交易输入数据模型"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransactionInput(BaseModel):
    """交易输入数据模型（加强安全验证）"""

    transaction_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
        examples=["TX20260623001"],
        description="交易ID，只能包含字母、数字、下划线和短横线"
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
        examples=["U10086"],
        description="用户ID"
    )

    merchant_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
        examples=["M2033"],
        description="商户ID"
    )

    amount: float = Field(
        ...,
        gt=0,
        le=999999999.99,
        examples=[9800],
        description="交易金额，必须大于0且不超过10亿"
    )

    currency: str = Field(
        default="CNY",
        pattern=r"^[A-Z]{3}$",
        examples=["CNY"],
        description="货币代码，ISO 4217 标准（如 CNY、USD）"
    )

    account_age_days: int = Field(
        ...,
        ge=0,
        le=36500,
        examples=[3],
        description="账户年龄（天），最大36500天（100年）"
    )

    transaction_frequency_1h: int = Field(
        ...,
        ge=0,
        le=1000,
        examples=[12],
        description="1小时内交易次数，最大1000次"
    )

    ip_location_status: Literal["normal", "abnormal"] = Field(
        ...,
        examples=["abnormal"],
        description="IP地址状态"
    )

    device_status: Literal["normal", "abnormal"] = Field(
        ...,
        examples=["abnormal"],
        description="设备状态"
    )

    kyc_status: Literal["verified", "basic_verified", "unverified"] = Field(
        ...,
        examples=["basic_verified"],
        description="KYC认证状态"
    )

    merchant_risk_level: Literal["low", "medium", "high"] = Field(
        ...,
        examples=["medium"],
        description="商户风险等级"
    )

    is_blacklisted: bool = Field(
        default=False,
        examples=[False],
        description="是否在黑名单中"
    )

    timestamp: datetime = Field(
        ...,
        examples=["2026-06-23T10:30:00"],
        description="交易时间戳"
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """验证时间戳的合理性"""
        from datetime import timezone, timedelta

        now = datetime.now(timezone.utc)

        # 确保时间戳有时区信息
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        # 检查时间戳不能是未来时间（允许5分钟误差）
        if v > now + timedelta(minutes=5):
            raise ValueError("Transaction timestamp cannot be in the future")

        # 检查时间戳不能太旧（不超过30天）
        if v < now - timedelta(days=30):
            raise ValueError("Transaction timestamp is too old (exceeds 30 days)")

        return v

    # 可选字段：用于高级风控分析
    device_id: str | None = Field(
        default=None,
        max_length=200,
        examples=["device_abc123xyz"],
        description="设备唯一标识符（用于设备指纹分析）"
    )

    ip_address: str | None = Field(
        default=None,
        max_length=45,
        examples=["192.168.1.100"],
        description="IP地址（支持IPv4和IPv6）"
    )

    user_agent: str | None = Field(
        default=None,
        max_length=500,
        examples=["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"],
        description="用户代理字符串（浏览器指纹）"
    )

    transaction_frequency_24h: int | None = Field(
        default=None,
        ge=0,
        le=10000,
        examples=[45],
        description="24小时内交易次数"
    )

    transaction_frequency_7d: int | None = Field(
        default=None,
        ge=0,
        le=100000,
        examples=[150],
        description="7天内交易次数"
    )

    merchant_category: str | None = Field(
        default=None,
        max_length=100,
        examples=["electronics", "crypto", "gambling"],
        description="商户类别（用于高风险行业识别）"
    )

    is_cross_border: bool = Field(
        default=False,
        examples=[False],
        description="是否跨境交易"
    )

    chargeback_history: int = Field(
        default=0,
        ge=0,
        le=1000,
        examples=[0],
        description="历史退单次数"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """验证交易金额精度（最多2位小数）"""
        if round(v, 2) != v:
            raise ValueError("交易金额最多支持2位小数")
        return v
