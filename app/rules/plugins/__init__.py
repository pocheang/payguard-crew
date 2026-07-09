"""
规则插件包

自动注册所有规则插件
"""
from app.rules.plugins.base import get_rule_registry
from app.rules.plugins.basic_rules import (
    NewAccountHighAmountRule,
    HighFrequencyRule,
    AbnormalIPRule,
    IncompleteKYCRule,
    HighRiskMerchantRule,
    AbnormalDeviceRule,
    BlacklistRule,
)
from app.rules.plugins.advanced_rules import (
    AccountTakeoverRule,
    CardTestingRule,
    VelocityAbuseRule,
    HighRiskIndustryRule,
    NewAccountVelocityRule,
    LargeAmountFrequencyRule,
)

# 自动注册所有规则
registry = get_rule_registry()

# 基础规则（7个）
registry.register(NewAccountHighAmountRule())
registry.register(HighFrequencyRule())
registry.register(AbnormalIPRule())
registry.register(IncompleteKYCRule())
registry.register(HighRiskMerchantRule())
registry.register(AbnormalDeviceRule())
registry.register(BlacklistRule())

# 高级规则（6个）
registry.register(AccountTakeoverRule())
registry.register(CardTestingRule())
registry.register(VelocityAbuseRule())
registry.register(HighRiskIndustryRule())
registry.register(NewAccountVelocityRule())
registry.register(LargeAmountFrequencyRule())

__all__ = ["get_rule_registry"]
