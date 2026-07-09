"""
基础风险规则插件

包含：新账户、高频交易、IP异常、KYC、商户风险、设备异常
"""
from app.rules.plugins.base import RulePlugin
from app.schemas.transaction import TransactionInput


class NewAccountHighAmountRule(RulePlugin):
    """R001: 新账户大额交易"""

    rule_id = "R001"
    rule_name = "new_account_high_amount"
    priority = 5

    def evaluate(self, tx: TransactionInput):
        if tx.account_age_days < 7 and tx.amount > 5000:
            return self.to_dict("账户注册小于7天且交易金额超过5000", 25)
        return None


class HighFrequencyRule(RulePlugin):
    """R002: 高频交易"""

    rule_id = "R002"
    rule_name = "high_frequency_transaction"
    priority = 3

    def evaluate(self, tx: TransactionInput):
        if tx.transaction_frequency_1h > 10:
            return self.to_dict("1小时内交易次数超过10次", 20)
        return None


class AbnormalIPRule(RulePlugin):
    """R003: IP地址异常"""

    rule_id = "R003"
    rule_name = "abnormal_ip_location"
    priority = 3

    def evaluate(self, tx: TransactionInput):
        if tx.ip_location_status == "abnormal":
            return self.to_dict("交易IP地区异常", 15)
        return None


class IncompleteKYCRule(RulePlugin):
    """R004: KYC未完整"""

    rule_id = "R004"
    rule_name = "incomplete_kyc_high_amount"
    priority = 4

    def evaluate(self, tx: TransactionInput):
        if tx.kyc_status != "verified" and tx.amount > 3000:
            return self.to_dict("KYC未完整认证且交易金额超过3000", 20)
        return None


class HighRiskMerchantRule(RulePlugin):
    """R005: 高风险商户"""

    rule_id = "R005"
    rule_name = "high_risk_merchant"
    priority = 6

    def evaluate(self, tx: TransactionInput):
        if tx.merchant_risk_level == "high":
            return self.to_dict("商户风险等级为 high", 25)
        return None


class AbnormalDeviceRule(RulePlugin):
    """R006: 设备异常"""

    rule_id = "R006"
    rule_name = "abnormal_device"
    priority = 3

    def evaluate(self, tx: TransactionInput):
        if tx.device_status == "abnormal":
            return self.to_dict("交易设备状态异常", 15)
        return None


class BlacklistRule(RulePlugin):
    """R007: 黑名单"""

    rule_id = "R007"
    rule_name = "blacklist_hit"
    priority = 100  # 最高优先级

    def evaluate(self, tx: TransactionInput):
        if tx.is_blacklisted:
            return self.to_dict("用户、设备或商户命中黑名单", 100)
        return None
