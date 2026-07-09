"""
高级风险规则插件

包含：账户接管、卡测试、速度滥用、高风险行业等复合模式
"""
from app.rules.plugins.base import RulePlugin
from app.schemas.transaction import TransactionInput


class AccountTakeoverRule(RulePlugin):
    """R008: 账户接管模式"""

    rule_id = "R008"
    rule_name = "account_takeover_pattern"
    priority = 8

    def evaluate(self, tx: TransactionInput):
        if tx.device_status == "abnormal" and tx.ip_location_status == "abnormal":
            return self.to_dict("设备和IP同时异常，疑似账户接管", 30)
        return None


class CardTestingRule(RulePlugin):
    """R009: 卡测试模式"""

    rule_id = "R009"
    rule_name = "card_testing_pattern"
    priority = 7

    def evaluate(self, tx: TransactionInput):
        if tx.transaction_frequency_1h > 10 and tx.amount < 100:
            return self.to_dict("高频小额交易，疑似卡测试", 25)
        return None


class VelocityAbuseRule(RulePlugin):
    """R010: 速度滥用"""

    rule_id = "R010"
    rule_name = "velocity_abuse"
    priority = 9

    def evaluate(self, tx: TransactionInput):
        if tx.transaction_frequency_1h > 20:
            return self.to_dict("1小时内交易超过20次，严重违反速度限制", 35)
        return None


class HighRiskIndustryRule(RulePlugin):
    """R011: 高风险行业"""

    rule_id = "R011"
    rule_name = "high_risk_industry"
    priority = 7

    def evaluate(self, tx: TransactionInput):
        high_risk_prefixes = ["M999", "M888", "M777"]
        if any(tx.merchant_id.startswith(prefix) for prefix in high_risk_prefixes):
            return self.to_dict("商户属于高风险行业（加密/博彩/成人）", 30)
        return None


class NewAccountVelocityRule(RulePlugin):
    """R012: 新账户速度滥用"""

    rule_id = "R012"
    rule_name = "new_account_velocity"
    priority = 6

    def evaluate(self, tx: TransactionInput):
        if tx.account_age_days < 7 and tx.transaction_frequency_1h > 5:
            return self.to_dict("新账户高频交易，疑似批量欺诈", 25)
        return None


class LargeAmountFrequencyRule(RulePlugin):
    """R013: 大额高频"""

    rule_id = "R013"
    rule_name = "large_amount_frequency"
    priority = 7

    def evaluate(self, tx: TransactionInput):
        if tx.amount > 10000 and tx.transaction_frequency_1h > 3:
            return self.to_dict("短时间内多笔大额交易", 30)
        return None
