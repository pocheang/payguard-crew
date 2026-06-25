"""
输入验证和错误处理优化

问题修复:
1. ❌ 缺少输入数据边界检查
2. ❌ 没有异常交易金额验证
3. ❌ 缺少频率限制验证
4. ❌ 错误信息不够详细

优化方案:
1. ✅ 添加全面的输入验证
2. ✅ 业务规则验证
3. ✅ 详细的错误信息
4. ✅ 数据清洗和规范化
"""
from typing import Any
from pydantic import ValidationError
from app.schemas.transaction import TransactionInput


class ValidationException(Exception):
    """验证异常"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class TransactionValidator:
    """交易验证器"""
    
    # 业务规则常量
    MAX_AMOUNT = 1_000_000.0  # 单笔最大金额
    MAX_FREQUENCY_1H = 100    # 1小时最大交易次数
    MAX_FREQUENCY_24H = 500   # 24小时最大交易次数
    MAX_ACCOUNT_AGE = 36500   # 最大账户年龄（100年）
    
    @staticmethod
    def validate_amount(amount: float) -> None:
        """验证交易金额"""
        if amount <= 0:
            raise ValidationException("amount", "交易金额必须大于0", amount)
        
        if amount > TransactionValidator.MAX_AMOUNT:
            raise ValidationException(
                "amount",
                f"交易金额超过限额 {TransactionValidator.MAX_AMOUNT}",
                amount
            )
        
        # 检查小数精度
        if round(amount, 2) != amount:
            raise ValidationException("amount", "交易金额最多支持2位小数", amount)
    
    @staticmethod
    def validate_frequency(frequency: int, max_frequency: int, period: str) -> None:
        """验证交易频率"""
        if frequency < 0:
            raise ValidationException(
                f"transaction_frequency_{period}",
                "交易频率不能为负数",
                frequency
            )
        
        if frequency > max_frequency:
            raise ValidationException(
                f"transaction_frequency_{period}",
                f"{period}交易频率超过限制 {max_frequency}",
                frequency
            )
    
    @staticmethod
    def validate_account_age(account_age_days: int) -> None:
        """验证账户年龄"""
        if account_age_days < 0:
            raise ValidationException("account_age_days", "账户年龄不能为负数", account_age_days)
        
        if account_age_days > TransactionValidator.MAX_ACCOUNT_AGE:
            raise ValidationException(
                "account_age_days",
                f"账户年龄超过最大值 {TransactionValidator.MAX_ACCOUNT_AGE}",
                account_age_days
            )
    
    @staticmethod
    def validate_merchant_id(merchant_id: str) -> None:
        """验证商户ID"""
        if not merchant_id or not merchant_id.strip():
            raise ValidationException("merchant_id", "商户ID不能为空", merchant_id)
        
        if len(merchant_id) > 100:
            raise ValidationException("merchant_id", "商户ID长度不能超过100", merchant_id)
        
        # 检查格式
        if not merchant_id.replace("_", "").replace("-", "").isalnum():
            raise ValidationException(
                "merchant_id",
                "商户ID只能包含字母、数字、下划线和短横线",
                merchant_id
            )
    
    @staticmethod
    def validate_transaction_id(transaction_id: str) -> None:
        """验证交易ID"""
        if not transaction_id or not transaction_id.strip():
            raise ValidationException("transaction_id", "交易ID不能为空", transaction_id)
        
        if len(transaction_id) > 100:
            raise ValidationException("transaction_id", "交易ID长度不能超过100", transaction_id)
        
        # 检查格式
        if not transaction_id.replace("_", "").replace("-", "").isalnum():
            raise ValidationException(
                "transaction_id",
                "交易ID只能包含字母、数字、下划线和短横线",
                transaction_id
            )
    
    @staticmethod
    def validate_transaction(tx: TransactionInput) -> None:
        """
        验证完整交易数据
        
        Raises:
            ValidationException: 验证失败时抛出
        """
        # 基础验证
        TransactionValidator.validate_transaction_id(tx.transaction_id)
        TransactionValidator.validate_merchant_id(tx.merchant_id)
        TransactionValidator.validate_amount(tx.amount)
        TransactionValidator.validate_account_age(tx.account_age_days)
        
        # 频率验证
        TransactionValidator.validate_frequency(
            tx.transaction_frequency_1h,
            TransactionValidator.MAX_FREQUENCY_1H,
            "1h"
        )
        
        if tx.transaction_frequency_24h is not None:
            TransactionValidator.validate_frequency(
                tx.transaction_frequency_24h,
                TransactionValidator.MAX_FREQUENCY_24H,
                "24h"
            )
        
        # 业务规则验证
        TransactionValidator.validate_business_rules(tx)
    
    @staticmethod
    def validate_business_rules(tx: TransactionInput) -> None:
        """验证业务规则"""
        # 24小时频率应该 >= 1小时频率
        if tx.transaction_frequency_24h is not None:
            if tx.transaction_frequency_24h < tx.transaction_frequency_1h:
                raise ValidationException(
                    "transaction_frequency",
                    "24小时交易频率不能小于1小时交易频率",
                    f"24h:{tx.transaction_frequency_24h} < 1h:{tx.transaction_frequency_1h}"
                )
        
        # 7天频率应该 >= 24小时频率
        if tx.transaction_frequency_7d is not None and tx.transaction_frequency_24h is not None:
            if tx.transaction_frequency_7d < tx.transaction_frequency_24h:
                raise ValidationException(
                    "transaction_frequency",
                    "7天交易频率不能小于24小时交易频率",
                    f"7d:{tx.transaction_frequency_7d} < 24h:{tx.transaction_frequency_24h}"
                )


def validate_and_sanitize_transaction(tx_data: dict) -> TransactionInput:
    """
    验证并清洗交易数据
    
    Args:
        tx_data: 原始交易数据
        
    Returns:
        验证后的TransactionInput对象
        
    Raises:
        ValidationException: 验证失败
        ValueError: 数据格式错误
    """
    try:
        # Pydantic 验证
        tx = TransactionInput(**tx_data)
        
        # 自定义业务验证
        TransactionValidator.validate_transaction(tx)
        
        return tx
        
    except ValidationError as e:
        # 转换 Pydantic 错误为友好格式
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"{field}: {message}")
        raise ValueError(f"数据验证失败: {'; '.join(errors)}")
    
    except ValidationException:
        raise
    
    except Exception as e:
        raise ValueError(f"交易数据格式错误: {str(e)}")
