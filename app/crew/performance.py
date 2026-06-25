"""
性能优化工具 - 缓存、连接池、批处理
"""
from functools import lru_cache
from typing import Any, Callable
import time


class PerformanceOptimizer:
    """性能优化器 - 提供缓存、批处理等优化功能"""
    
    def __init__(self):
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_time_saved_ms": 0,
        }
    
    @staticmethod
    def cached_function(maxsize: int = 128, ttl: int = 300):
        """
        带TTL的LRU缓存装饰器
        
        Args:
            maxsize: 缓存大小
            ttl: 缓存过期时间（秒）
        """
        def decorator(func: Callable) -> Callable:
            # 使用lru_cache包装
            cached_func = lru_cache(maxsize=maxsize)(func)
            cached_func.cache_expiry = {}
            
            def wrapper(*args, **kwargs):
                # 构建缓存键
                cache_key = str(args) + str(kwargs)
                current_time = time.time()
                
                # 检查缓存是否过期
                if cache_key in cached_func.cache_expiry:
                    if current_time - cached_func.cache_expiry[cache_key] > ttl:
                        # 缓存过期，清除
                        cached_func.cache_clear()
                        cached_func.cache_expiry.clear()
                
                # 记录访问时间
                result = cached_func(*args, **kwargs)
                cached_func.cache_expiry[cache_key] = current_time
                
                return result
            
            wrapper.cache_info = cached_func.cache_info
            wrapper.cache_clear = cached_func.cache_clear
            return wrapper
        
        return decorator
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100, processor: Callable = None) -> list:
        """
        批量处理数据
        
        Args:
            items: 要处理的数据列表
            batch_size: 每批次大小
            processor: 处理函数
            
        Returns:
            处理后的结果列表
        """
        if not processor:
            return items
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = processor(batch)
            results.extend(batch_results)
        
        return results
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self._cache_stats.copy()
    
    def reset_cache_stats(self):
        """重置缓存统计"""
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_time_saved_ms": 0,
        }


# 全局优化器实例
_optimizer = PerformanceOptimizer()


def get_optimizer() -> PerformanceOptimizer:
    """获取全局优化器实例"""
    return _optimizer


# 常用的缓存装饰器
def cache_result(maxsize: int = 128, ttl: int = 300):
    """缓存函数结果（便捷装饰器）"""
    return PerformanceOptimizer.cached_function(maxsize=maxsize, ttl=ttl)


# 规则引擎结果缓存（用于相同交易的重复评估）
@lru_cache(maxsize=1000)
def cache_rule_evaluation(transaction_hash: str) -> dict:
    """缓存规则评估结果（需要配合实际使用）"""
    # 这是一个占位函数，实际使用时在risk_rules.py中调用
        # 空实现
# Agent注册表缓存（避免重复构建）
_agent_registry_cache: dict[str, Any] | None = None


def get_cached_agent_registry(builder: Callable) -> dict:
    """获取缓存的Agent注册表"""
    global _agent_registry_cache
    if _agent_registry_cache is None:
        _agent_registry_cache = builder()
    return _agent_registry_cache


def clear_agent_registry_cache():
    """清除Agent注册表缓存"""
    global _agent_registry_cache
    _agent_registry_cache = None
