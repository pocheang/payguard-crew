"""
Redis缓存管理模块

提供统一的缓存接口，支持：
- 审计结果缓存
- 统计数据缓存
- 规则配置缓存
- 会话管理
"""
import json
import pickle
from typing import Optional, Any, List
from functools import wraps
import hashlib

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from app.core.environment import get_env


class CacheManager:
    """Redis缓存管理器"""

    def __init__(self):
        self.client: Optional[Redis] = None
        self.enabled = False
        self._initialize()

    def _initialize(self):
        """初始化Redis连接"""
        if not REDIS_AVAILABLE:
            print("Redis not installed, caching disabled")
            return

        redis_url = get_env("REDIS_URL", "redis://localhost:6379/0")

        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=False,  # 使用bytes模式以支持pickle
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            self.enabled = True
            print(f"✓ Redis connected: {redis_url}")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            self.enabled = False
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.enabled:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒），默认5分钟
        """
        if not self.enabled:
            return False

        try:
            serialized = pickle.dumps(value)
            self.client.setex(key, expire, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """批量删除匹配的键"""
        if not self.enabled:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete_pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.enabled:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    def increment(self, key: str, amount: int = 1, expire: int = 3600) -> Optional[int]:
        """
        原子递增计数器

        Args:
            key: 计数器键
            amount: 递增量
            expire: 首次创建时的过期时间
        """
        if not self.enabled:
            return None

        try:
            value = self.client.incr(key, amount)
            # 如果是新创建的键，设置过期时间
            if value == amount:
                self.client.expire(key, expire)
            return value
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None

    def get_many(self, keys: List[str]) -> dict:
        """批量获取缓存"""
        if not self.enabled:
            return {}

        try:
            values = self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = pickle.loads(value)
            return result
        except Exception as e:
            print(f"Cache get_many error: {e}")
            return {}

    def set_many(self, mapping: dict, expire: int = 300) -> bool:
        """批量设置缓存"""
        if not self.enabled:
            return False

        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                serialized = pickle.dumps(value)
                pipe.setex(key, expire, serialized)
            pipe.execute()
            return True
        except Exception as e:
            print(f"Cache set_many error: {e}")
            return False

    def clear_all(self) -> bool:
        """清空所有缓存（慎用！）"""
        if not self.enabled:
            return False

        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear_all error: {e}")
            return False


# 全局缓存实例
cache = CacheManager()


def cache_key(*args, prefix: str = "payguard") -> str:
    """
    生成缓存键

    Example:
        cache_key("audit", transaction_id) -> "payguard:audit:abc123"
    """
    parts = [prefix] + [str(arg) for arg in args]
    return ":".join(parts)


def cache_result(expire: int = 300, key_prefix: str = "result"):
    """
    缓存函数结果的装饰器

    Args:
        expire: 过期时间（秒）
        key_prefix: 缓存键前缀

    Example:
        @cache_result(expire=600, key_prefix="statistics")
        def get_statistics():
            return expensive_calculation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键（基于函数名和参数）
            args_str = json.dumps([args, kwargs], sort_keys=True, default=str)
            key_hash = hashlib.md5(args_str.encode()).hexdigest()
            key = cache_key(key_prefix, func.__name__, key_hash)

            # 尝试从缓存获取
            cached = cache.get(key)
            if cached is not None:
                return cached

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(key, result, expire)
            return result

        return wrapper
    return decorator


# 便捷方法

def cache_audit_result(transaction_id: str, result: dict, expire: int = 3600):
    """缓存审计结果（1小时）"""
    key = cache_key("audit", transaction_id)
    return cache.set(key, result, expire)


def get_cached_audit(transaction_id: str) -> Optional[dict]:
    """获取缓存的审计结果"""
    key = cache_key("audit", transaction_id)
    return cache.get(key)


def cache_statistics(stats: dict, expire: int = 300):
    """缓存统计数据（5分钟）"""
    key = cache_key("statistics", "global")
    return cache.set(key, stats, expire)


def get_cached_statistics() -> Optional[dict]:
    """获取缓存的统计数据"""
    key = cache_key("statistics", "global")
    return cache.get(key)


def invalidate_audit_cache(transaction_id: str = None):
    """使审计缓存失效"""
    if transaction_id:
        key = cache_key("audit", transaction_id)
        cache.delete(key)
    else:
        # 清空所有审计缓存
        pattern = cache_key("audit", "*")
        cache.delete_pattern(pattern)


def invalidate_statistics_cache():
    """使统计缓存失效"""
    pattern = cache_key("statistics", "*")
    cache.delete_pattern(pattern)
