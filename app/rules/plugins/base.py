"""
规则引擎插件基类

设计原则：
1. 每个规则是一个独立的类，易于测试
2. 支持热插拔（动态加载/卸载规则）
3. 规则可配置优先级、启用/禁用
"""
from abc import ABC, abstractmethod
from typing import Any
from app.schemas.transaction import TransactionInput


class RulePlugin(ABC):
    """规则插件基类"""

    # 规则元数据
    rule_id: str = ""
    rule_name: str = ""
    priority: int = 0  # 数字越大优先级越高
    enabled: bool = True

    @abstractmethod
    def evaluate(self, tx: TransactionInput) -> dict[str, Any] | None:
        """
        评估规则

        Args:
            tx: 交易输入

        Returns:
            如果规则触发，返回 {"rule_id": "R001", "rule_name": "...", "reason": "...", "score": 25, "priority": 5}
            如果规则不触发，返回 None
        """
        pass

    def to_dict(self, reason: str, score: int) -> dict[str, Any]:
        """辅助方法：生成规则字典"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "reason": reason,
            "score": score,
            "priority": self.priority,
        }


class RuleRegistry:
    """规则注册表"""

    def __init__(self):
        self._rules: dict[str, RulePlugin] = {}

    def register(self, rule: RulePlugin) -> None:
        """注册规则"""
        self._rules[rule.rule_id] = rule

    def unregister(self, rule_id: str) -> None:
        """注销规则"""
        self._rules.pop(rule_id, None)

    def get_all_rules(self) -> list[RulePlugin]:
        """获取所有启用的规则"""
        return [r for r in self._rules.values() if r.enabled]

    def get_rule(self, rule_id: str) -> RulePlugin | None:
        """获取指定规则"""
        return self._rules.get(rule_id)


# 全局规则注册表
_global_registry = RuleRegistry()


def get_rule_registry() -> RuleRegistry:
    """获取全局规则注册表"""
    return _global_registry
