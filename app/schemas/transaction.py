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
