"""查询构建工具"""
from typing import Any, List, Tuple


class QueryBuilder:
    """动态SQL查询构建器"""

    def __init__(self, base_table: str, select_clause: str = "*"):
        """
        初始化查询构建器

        Args:
            base_table: 基础表名
            select_clause: SELECT子句（默认为*）
        """
        self.base_table = base_table
        self.select_clause = select_clause
        self.query = f"SELECT {select_clause} FROM {base_table} WHERE 1=1"
        self.params: List[Any] = []

    def add_filter(self, column: str, value: Any, operator: str = "=") -> 'QueryBuilder':
        """
        添加过滤条件

        Args:
            column: 列名
            value: 值（如果为None则跳过）
            operator: 操作符（默认为=）

        Returns:
            self（支持链式调用）
        """
        if value is not None:
            self.query += f" AND {column} {operator} ?"
            self.params.append(value)
        return self

    def add_order_by(self, column: str, direction: str = "DESC") -> 'QueryBuilder':
        """添加排序"""
        self.query += f" ORDER BY {column} {direction}"
        return self

    def add_limit(self, limit: int, offset: int = 0) -> 'QueryBuilder':
        """添加分页"""
        self.query += f" LIMIT ? OFFSET ?"
        self.params.extend([limit, offset])
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """构建最终查询"""
        return self.query, self.params

    def get_count_query(self) -> Tuple[str, List[Any]]:
        """
        获取计数查询（不包含ORDER BY和LIMIT）

        Returns:
            计数查询和参数
        """
        # 移除ORDER BY和LIMIT子句
        base_query = self.query.split(" ORDER BY")[0].split(" LIMIT")[0]
        count_query = base_query.replace(f"SELECT {self.select_clause}", "SELECT COUNT(*) as count")

        # 只返回过滤参数（不包含LIMIT/OFFSET参数）
        if " LIMIT " in self.query:
            # 去掉最后两个参数（limit和offset）
            count_params = self.params[:-2]
        else:
            count_params = self.params

        return count_query, count_params
