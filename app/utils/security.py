"""
安全漏洞修复方案

发现的问题:
1. ❌ SQL注入风险 - transaction_id未验证
2. ❌ 缺少速率限制 - API可被滥用
3. ❌ 错误信息泄露 - 暴露内部实现
4. ❌ 缺少请求大小限制
5. ❌ 时间戳验证缺失

修复方案:
1. ✅ 输入清洗和验证
2. ✅ API速率限制
3. ✅ 安全的错误处理
4. ✅ 请求大小限制
5. ✅ 时间戳验证
"""
import re
from typing import Optional
from datetime import datetime, timezone, timedelta


class SecurityValidator:
    """安全验证器"""
    
    # 安全常量
    MAX_TRANSACTION_ID_LENGTH = 100
    MAX_STRING_LENGTH = 1000
    TRANSACTION_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')
    
    @staticmethod
    def sanitize_transaction_id(transaction_id: str) -> str:
        """
        清洗交易ID，防止SQL注入
        
        Raises:
            ValueError: 如果transaction_id不安全
        """
        if not transaction_id:
            raise ValueError("交易ID不能为空")
        
        # 检查长度
        if len(transaction_id) > SecurityValidator.MAX_TRANSACTION_ID_LENGTH:
            raise ValueError(f"交易ID长度不能超过{SecurityValidator.MAX_TRANSACTION_ID_LENGTH}")
        
        # 检查格式（只允许字母、数字、下划线、短横线）
        if not SecurityValidator.TRANSACTION_ID_PATTERN.match(transaction_id):
            raise ValueError("交易ID只能包含字母、数字、下划线和短横线")
        
        return transaction_id.strip()
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = MAX_STRING_LENGTH) -> str:
        """清洗字符串，防止注入攻击"""
        if not value:
            return ""
        
        # 检查长度
        if len(value) > max_length:
            raise ValueError(f"字符串长度不能超过{max_length}")
        
        # 移除危险字符
        sanitized = value.strip()
        
        # 检查SQL注入特征
        sql_patterns = [
            r";\s*DROP\s+TABLE",
            r";\s*DELETE\s+FROM",
            r";\s*UPDATE\s+",
            r"--",
            r"/\*.*?\*/",
            r"'\s*OR\s+'.*?'\s*=\s*'",
            r"UNION\s+SELECT",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("检测到潜在的SQL注入攻击")
        
        return sanitized
    
    @staticmethod
    def validate_timestamp(timestamp: datetime) -> None:
        """验证时间戳的合理性"""
        now = datetime.now(timezone.utc)
        
        # 检查时间戳不能是未来时间（允许5分钟误差）
        if timestamp > now + timedelta(minutes=5):
            raise ValueError("时间戳不能是未来时间")
        
        # 检查时间戳不能太旧（不超过30天）
        if timestamp < now - timedelta(days=30):
            raise ValueError("时间戳过旧（超过30天）")
    
    @staticmethod
    def validate_amount_range(amount: float) -> None:
        """验证金额范围的合理性"""
        if amount < 0:
            raise ValueError("交易金额不能为负数")
        
        if amount > 10_000_000:  # 1000万
            raise ValueError("单笔交易金额不能超过1000万")
        
        # 检查是否为异常值（如NaN、Infinity）
        if not isinstance(amount, (int, float)) or amount != amount:
            raise ValueError("交易金额格式错误")


class RateLimiter:
    """API速率限制器"""
    
    def __init__(self):
        self._requests: dict[str, list[datetime]] = {}
        self._max_requests_per_minute = 60
        self._max_requests_per_hour = 1000
    
    def check_rate_limit(self, client_id: str) -> tuple[bool, str]:
        """检查速率限制"""
        now = datetime.now(timezone.utc)
        
        # 初始化客户端记录
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        # 清理过期记录（超过1小时）
        self._requests[client_id] = [
            ts for ts in self._requests[client_id]
            if now - ts < timedelta(hours=1)
        ]
        
        # 检查每分钟限制
        recent_minute = [
            ts for ts in self._requests[client_id]
            if now - ts < timedelta(minutes=1)
        ]
        if len(recent_minute) >= self._max_requests_per_minute:
            return False, f"超过每分钟请求限制({self._max_requests_per_minute}次)"
        
        # 检查每小时限制
        if len(self._requests[client_id]) >= self._max_requests_per_hour:
            return False, f"超过每小时请求限制({self._max_requests_per_hour}次)"
        
        # 记录本次请求
        self._requests[client_id].append(now)
        
        return True, ""


# 全局速率限制器
_global_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """获取全局速率限制器"""
    return _global_rate_limiter


def safe_error_message(error: Exception, include_details: bool = False) -> str:
    """生成安全的错误消息（不泄露内部实现）"""
    if not include_details:
        error_type = type(error).__name__
        
        safe_messages = {
            "ValidationError": "请求数据验证失败，请检查输入格式",
            "ValueError": "请求参数不合法",
            "KeyError": "缺少必需的参数",
            "TypeError": "参数类型错误",
            "HTTPException": str(error),
        }
        
        return safe_messages.get(error_type, "系统处理请求时发生错误，请稍后重试")
    
    return f"{type(error).__name__}: {str(error)}"
