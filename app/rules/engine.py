"""
插件化规则引擎（V2版本）

优势：
1. 每个规则独立文件，易于测试和维护
2. 支持动态加载/卸载规则
3. 单文件不超过200行
4. 易于扩展：只需继承RulePlugin并注册
"""
from app.schemas.transaction import TransactionInput
from app.rules.plugins import get_rule_registry

# 规则评估结果缓存
_risk_evaluation_cache: dict[str, dict] = {}


def _get_transaction_cache_key(tx: TransactionInput) -> str:
    """生成交易缓存键"""
    return (
        f"{tx.transaction_id}_{tx.account_age_days}_{tx.amount}_{tx.transaction_frequency_1h}_"
        f"{tx.ip_location_status}_{tx.device_status}_{tx.kyc_status}_{tx.merchant_risk_level}_"
        f"{tx.merchant_id}_{tx.is_blacklisted}"
    )


def _deduplicate_rules(rules: list[dict]) -> list[dict]:
    """
    规则去重，保留高优先级规则

    规则冲突映射：高级规则覆盖基础规则
    """
    if not rules:
        return rules

    # 按优先级排序
    sorted_rules = sorted(rules, key=lambda r: (-r.get("priority", 0), r["rule_id"]))

    # 规则冲突映射
    conflicts = {
        "R008": ["R003", "R006"],  # 账户接管覆盖IP和设备异常
        "R009": ["R002"],          # 卡测试覆盖高频交易
        "R010": ["R002"],          # 速度滥用覆盖高频交易
    }

    excluded_ids = set()
    for rule in sorted_rules:
        if rule["rule_id"] in conflicts:
            excluded_ids.update(conflicts[rule["rule_id"]])

    return [r for r in sorted_rules if r["rule_id"] not in excluded_ids]


def evaluate_risk(tx: TransactionInput) -> dict:
    """
    插件化风险评估

    优化点：
    1. 缓存检查
    2. 黑名单早期返回
    3. 插件化规则执行
    4. 规则去重

    返回：
        {
            "risk_score": int,
            "risk_level": str,
            "decision": str,
            "triggered_rules": list[dict],
            "requires_manual_review": bool
        }
    """
    # 检查缓存
    cache_key = _get_transaction_cache_key(tx)
    if cache_key in _risk_evaluation_cache:
        return _risk_evaluation_cache[cache_key].copy()

    registry = get_rule_registry()
    triggered_rules = []

    # 执行所有启用的规则
    for rule in registry.get_all_rules():
        result = rule.evaluate(tx)
        if result:
            triggered_rules.append(result)

            # 黑名单早期返回
            if rule.rule_id == "R007":
                early_result = {
                    "risk_score": 100,
                    "risk_level": "high",
                    "decision": "reject",
                    "triggered_rules": [result],
                    "requires_manual_review": True,
                }
                _risk_evaluation_cache[cache_key] = early_result.copy()
                return early_result

    # 规则去重
    deduplicated_rules = _deduplicate_rules(triggered_rules)

    # 计算风险分数
    risk_score = min(sum(r["score"] for r in deduplicated_rules), 100)

    # 确定风险等级
    if risk_score >= 70:
        risk_level, decision, manual_review = "high", "review", True
    elif risk_score >= 30:
        risk_level, decision, manual_review = "medium", "review", True
    else:
        risk_level, decision, manual_review = "low", "approve", False

    result = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "triggered_rules": deduplicated_rules,
        "requires_manual_review": manual_review,
    }

    # 缓存管理
    if len(_risk_evaluation_cache) >= 1000:
        # 清理最旧的50%
        keys_to_remove = list(_risk_evaluation_cache.keys())[:500]
        for key in keys_to_remove:
            del _risk_evaluation_cache[key]

    _risk_evaluation_cache[cache_key] = result.copy()
    return result


def build_rule_query(triggered_rules: list[dict], tx: TransactionInput) -> str:
    """构建RAG检索查询"""
    names = " ".join(rule["rule_name"] for rule in triggered_rules)
    return (
        f"{names} amount {tx.amount} account_age_days {tx.account_age_days} "
        f"kyc {tx.kyc_status} ip {tx.ip_location_status} device {tx.device_status} "
        f"merchant {tx.merchant_risk_level}"
    )
