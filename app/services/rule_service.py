"""
规则管理服务

提供完整的规则CRUD、版本管理、测试等功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.db.database import get_connection
from app.utils.datetime_utils import now_iso
from app.core.cache import cache, cache_key


class RuleStatus(str, Enum):
    """规则状态"""
    ACTIVE = "active"          # 激活
    INACTIVE = "inactive"      # 停用
    TESTING = "testing"        # 测试中
    ARCHIVED = "archived"      # 已归档


class RuleService:
    """规则管理服务"""

    @staticmethod
    def create_rule(
        name: str,
        description: str,
        rule_type: str,
        weight: int,
        condition: Dict[str, Any],
        action: Dict[str, Any],
        created_by: str
    ) -> dict:
        """
        创建规则

        Args:
            name: 规则名称
            description: 规则描述
            rule_type: 规则类型（amount/frequency/location/merchant）
            weight: 权重（1-10）
            condition: 触发条件（JSON）
            action: 执行动作（JSON）
            created_by: 创建人

        Returns:
            创建的规则
        """
        import json

        now = now_iso()
        rule_id = f"rule_{int(datetime.now().timestamp() * 1000)}"

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO rules (
                    rule_id, name, description, rule_type, weight,
                    condition_json, action_json, status, version,
                    created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule_id, name, description, rule_type, weight,
                    json.dumps(condition), json.dumps(action),
                    RuleStatus.INACTIVE, 1, created_by, now, now
                )
            )
            conn.commit()

        # 清除缓存
        RuleService._invalidate_cache()

        return RuleService.get_rule(rule_id)

    @staticmethod
    def get_rule(rule_id: str) -> Optional[dict]:
        """获取规则详情"""
        import json

        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM rules WHERE rule_id = ?",
                (rule_id,)
            ).fetchone()

        if not row:
            return None

        rule = dict(row)
        # 解析JSON字段
        rule['condition'] = json.loads(rule.get('condition_json', '{}'))
        rule['action'] = json.loads(rule.get('action_json', '{}'))

        return rule

    @staticmethod
    def list_rules(
        status: Optional[str] = None,
        rule_type: Optional[str] = None,
        include_archived: bool = False
    ) -> List[dict]:
        """
        查询规则列表

        Args:
            status: 过滤状态
            rule_type: 过滤类型
            include_archived: 是否包含已归档

        Returns:
            规则列表
        """
        import json

        query = "SELECT * FROM rules WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if rule_type:
            query += " AND rule_type = ?"
            params.append(rule_type)

        if not include_archived:
            query += " AND status != ?"
            params.append(RuleStatus.ARCHIVED)

        query += " ORDER BY weight DESC, created_at DESC"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        rules = []
        for row in rows:
            rule = dict(row)
            rule['condition'] = json.loads(rule.get('condition_json', '{}'))
            rule['action'] = json.loads(rule.get('action_json', '{}'))
            rules.append(rule)

        return rules

    @staticmethod
    def update_rule(
        rule_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> dict:
        """
        更新规则

        Args:
            rule_id: 规则ID
            updates: 更新字段
            updated_by: 更新人

        Returns:
            更新后的规则
        """
        import json

        # 构建更新语句
        allowed_fields = ['name', 'description', 'weight', 'condition', 'action', 'status']
        set_clauses = []
        params = []

        for field, value in updates.items():
            if field in allowed_fields:
                if field in ['condition', 'action']:
                    set_clauses.append(f"{field}_json = ?")
                    params.append(json.dumps(value))
                else:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)

        if not set_clauses:
            return RuleService.get_rule(rule_id)

        # 添加更新时间和更新人
        set_clauses.append("updated_at = ?")
        set_clauses.append("updated_by = ?")
        params.extend([now_iso(), updated_by])
        params.append(rule_id)

        query = f"UPDATE rules SET {', '.join(set_clauses)} WHERE rule_id = ?"

        with get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

        # 清除缓存
        RuleService._invalidate_cache()

        return RuleService.get_rule(rule_id)

    @staticmethod
    def delete_rule(rule_id: str, deleted_by: str) -> bool:
        """
        删除规则（软删除，标记为已归档）

        Args:
            rule_id: 规则ID
            deleted_by: 删除人

        Returns:
            是否成功
        """
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE rules
                SET status = ?, updated_at = ?, updated_by = ?
                WHERE rule_id = ?
                """,
                (RuleStatus.ARCHIVED, now_iso(), deleted_by, rule_id)
            )
            conn.commit()

        # 清除缓存
        RuleService._invalidate_cache()

        return True

    @staticmethod
    def activate_rule(rule_id: str, activated_by: str) -> dict:
        """激活规则"""
        return RuleService.update_rule(
            rule_id,
            {'status': RuleStatus.ACTIVE},
            activated_by
        )

    @staticmethod
    def deactivate_rule(rule_id: str, deactivated_by: str) -> dict:
        """停用规则"""
        return RuleService.update_rule(
            rule_id,
            {'status': RuleStatus.INACTIVE},
            deactivated_by
        )

    @staticmethod
    def test_rule(rule_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试规则

        Args:
            rule_id: 规则ID
            test_data: 测试数据

        Returns:
            测试结果
        """
        rule = RuleService.get_rule(rule_id)
        if not rule:
            return {'error': 'Rule not found'}

        # 模拟规则执行
        condition = rule['condition']
        result = {
            'rule_id': rule_id,
            'rule_name': rule['name'],
            'matched': False,
            'test_data': test_data,
            'message': ''
        }

        # 简单的条件匹配逻辑
        try:
            if rule['rule_type'] == 'amount':
                threshold = condition.get('threshold', 0)
                amount = test_data.get('amount', 0)
                result['matched'] = amount > threshold
                result['message'] = f"Amount {amount} {'>' if result['matched'] else '<='} threshold {threshold}"

            elif rule['rule_type'] == 'frequency':
                max_count = condition.get('max_count', 0)
                count = test_data.get('count', 0)
                result['matched'] = count > max_count
                result['message'] = f"Count {count} {'>' if result['matched'] else '<='} max {max_count}"

            else:
                result['message'] = 'Rule type not implemented in test mode'

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def create_rule_version(rule_id: str, created_by: str) -> dict:
        """
        创建规则版本

        Args:
            rule_id: 规则ID
            created_by: 创建人

        Returns:
            新版本规则
        """
        import json

        # 获取当前规则
        current_rule = RuleService.get_rule(rule_id)
        if not current_rule:
            raise ValueError(f"Rule not found: {rule_id}")

        # 创建新版本
        new_version = current_rule['version'] + 1
        now = now_iso()

        with get_connection() as conn:
            # 保存旧版本到历史表
            conn.execute(
                """
                INSERT INTO rule_versions (
                    rule_id, version, name, description, rule_type, weight,
                    condition_json, action_json, status, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule_id, current_rule['version'], current_rule['name'],
                    current_rule['description'], current_rule['rule_type'],
                    current_rule['weight'], current_rule['condition_json'],
                    current_rule['action_json'], current_rule['status'],
                    created_by, now
                )
            )

            # 更新主表版本号
            conn.execute(
                "UPDATE rules SET version = ?, updated_at = ? WHERE rule_id = ?",
                (new_version, now, rule_id)
            )

            conn.commit()

        return RuleService.get_rule(rule_id)

    @staticmethod
    def get_rule_versions(rule_id: str) -> List[dict]:
        """获取规则版本历史"""
        import json

        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM rule_versions
                WHERE rule_id = ?
                ORDER BY version DESC
                """,
                (rule_id,)
            ).fetchall()

        versions = []
        for row in rows:
            version = dict(row)
            version['condition'] = json.loads(version.get('condition_json', '{}'))
            version['action'] = json.loads(version.get('action_json', '{}'))
            versions.append(version)

        return versions

    @staticmethod
    def get_rule_statistics() -> Dict[str, Any]:
        """获取规则统计"""
        # 尝试从缓存获取
        cache_key_stats = cache_key("rules", "statistics")
        cached = cache.get(cache_key_stats)
        if cached:
            return cached

        with get_connection() as conn:
            # 按状态统计
            status_stats = conn.execute(
                """
                SELECT status, COUNT(*) as count
                FROM rules
                WHERE status != 'archived'
                GROUP BY status
                """
            ).fetchall()

            # 按类型统计
            type_stats = conn.execute(
                """
                SELECT rule_type, COUNT(*) as count
                FROM rules
                WHERE status = 'active'
                GROUP BY rule_type
                """
            ).fetchall()

            # 总数
            total = conn.execute(
                "SELECT COUNT(*) as count FROM rules WHERE status != 'archived'"
            ).fetchone()

        stats = {
            'total_rules': total['count'],
            'by_status': {row['status']: row['count'] for row in status_stats},
            'by_type': {row['rule_type']: row['count'] for row in type_stats}
        }

        # 缓存5分钟
        cache.set(cache_key_stats, stats, expire=300)

        return stats

    @staticmethod
    def _invalidate_cache():
        """清除规则相关缓存"""
        cache.delete_pattern("payguard:rules:*")


# 初始化规则表
def init_rules_tables():
    """初始化规则相关数据表"""
    with get_connection() as conn:
        # 规则主表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                rule_type TEXT NOT NULL,
                weight INTEGER DEFAULT 5,
                condition_json TEXT,
                action_json TEXT,
                status TEXT DEFAULT 'inactive',
                version INTEGER DEFAULT 1,
                created_by TEXT,
                updated_by TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 规则版本历史表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rule_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                name TEXT,
                description TEXT,
                rule_type TEXT,
                weight INTEGER,
                condition_json TEXT,
                action_json TEXT,
                status TEXT,
                created_by TEXT,
                created_at TEXT
            )
        """)

        conn.commit()
        print("✓ Rules tables initialized")
