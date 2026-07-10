"""
Prometheus监控指标

提供系统关键指标的监控
"""
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps


# ============================================
# 指标定义
# ============================================

# 请求计数器
request_count = Counter(
    'payguard_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

# 请求延迟直方图
request_latency = Histogram(
    'payguard_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint']
)

# 审计请求计数
audit_requests = Counter(
    'payguard_audit_requests_total',
    'Total audit requests',
    ['risk_level']
)

# 审核任务计数
review_tasks = Counter(
    'payguard_review_tasks_total',
    'Total review tasks',
    ['status']
)

# 缓存命中率
cache_hits = Counter('payguard_cache_hits_total', 'Cache hits')
cache_misses = Counter('payguard_cache_misses_total', 'Cache misses')

# 数据库查询延迟
db_query_duration = Histogram(
    'payguard_db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# 活跃WebSocket连接数
websocket_connections = Gauge(
    'payguard_websocket_connections',
    'Active WebSocket connections'
)

# 任务队列长度
task_queue_length = Gauge(
    'payguard_task_queue_length',
    'Task queue length',
    ['queue_name']
)

# 错误计数
error_count = Counter(
    'payguard_errors_total',
    'Total errors',
    ['error_type']
)


# ============================================
# 装饰器
# ============================================

def track_time(metric: Histogram):
    """
    追踪函数执行时间

    Usage:
        @track_time(request_latency.labels(method='POST', endpoint='/api/audit'))
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.observe(duration)
        return wrapper
    return decorator


def count_calls(metric: Counter):
    """
    计数函数调用次数

    Usage:
        @count_calls(audit_requests.labels(risk_level='high'))
        def process_audit():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            metric.inc()
            return result
        return wrapper
    return decorator


# ============================================
# 便捷函数
# ============================================

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """记录API请求"""
    request_count.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
    request_latency.labels(method=method, endpoint=endpoint).observe(duration)


def record_audit(risk_level: str):
    """记录审计请求"""
    audit_requests.labels(risk_level=risk_level).inc()


def record_review(status: str):
    """记录审核任务"""
    review_tasks.labels(status=status).inc()


def record_cache_hit():
    """记录缓存命中"""
    cache_hits.inc()


def record_cache_miss():
    """记录缓存未命中"""
    cache_misses.inc()


def record_error(error_type: str):
    """记录错误"""
    error_count.labels(error_type=error_type).inc()


def update_websocket_connections(count: int):
    """更新WebSocket连接数"""
    websocket_connections.set(count)


def update_task_queue_length(queue_name: str, length: int):
    """更新任务队列长度"""
    task_queue_length.labels(queue_name=queue_name).set(length)


# ============================================
# 指标端点
# ============================================

def get_metrics() -> Response:
    """
    获取Prometheus指标

    Returns:
        Prometheus格式的指标数据
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================
# 中间件集成示例
# ============================================

"""
在FastAPI中使用：

from app.core.metrics import record_request
import time

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    record_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )

    return response
"""
