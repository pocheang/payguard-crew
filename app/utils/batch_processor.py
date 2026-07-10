"""
批量操作优化模块

提供高效的批量处理能力：
- 批量审计优化
- 并发控制
- 进度追踪
- 错误处理
"""
import asyncio
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BatchResult:
    """批量操作结果"""
    total: int
    success: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, str]]
    duration_ms: int


class BatchProcessor:
    """批量处理器"""

    def __init__(self, max_workers: int = 10):
        """
        初始化批量处理器

        Args:
            max_workers: 最大并发数
        """
        self.max_workers = max_workers

    def process_batch(
        self,
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100
    ) -> BatchResult:
        """
        批量处理（多线程）

        Args:
            items: 待处理项目列表
            process_func: 处理函数
            batch_size: 每批大小

        Returns:
            批量处理结果
        """
        start_time = datetime.now()
        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 分批提交任务
            futures = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                for item in batch:
                    future = executor.submit(self._safe_process, process_func, item)
                    futures.append((future, item))

            # 收集结果
            for future, item in futures:
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.append(result)
                except Exception as e:
                    errors.append({
                        'item': str(item),
                        'error': str(e)
                    })

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return BatchResult(
            total=len(items),
            success=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
            duration_ms=int(duration)
        )

    def _safe_process(self, func: Callable, item: Any) -> Any:
        """安全执行处理函数"""
        try:
            return func(item)
        except Exception as e:
            print(f"Process error: {e}")
            raise

    async def process_batch_async(
        self,
        items: List[Any],
        process_func: Callable,
        concurrency: int = 10
    ) -> BatchResult:
        """
        批量处理（异步）

        Args:
            items: 待处理项目列表
            process_func: 异步处理函数
            concurrency: 并发数

        Returns:
            批量处理结果
        """
        start_time = datetime.now()
        results = []
        errors = []

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(concurrency)

        async def process_with_semaphore(item):
            async with semaphore:
                try:
                    result = await process_func(item)
                    results.append(result)
                except Exception as e:
                    errors.append({
                        'item': str(item),
                        'error': str(e)
                    })

        # 并发执行所有任务
        tasks = [process_with_semaphore(item) for item in items]
        await asyncio.gather(*tasks, return_exceptions=True)

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return BatchResult(
            total=len(items),
            success=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
            duration_ms=int(duration)
        )


class ChunkedIterator:
    """分块迭代器 - 用于处理大数据集"""

    def __init__(self, items: List[Any], chunk_size: int = 100):
        self.items = items
        self.chunk_size = chunk_size
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration

        chunk = self.items[self.index:self.index + self.chunk_size]
        self.index += self.chunk_size
        return chunk


def batch_insert_optimized(records: List[Dict[str, Any]], table: str) -> int:
    """
    优化的批量插入（使用事务和批量提交）

    Args:
        records: 记录列表
        table: 表名

    Returns:
        插入的记录数
    """
    from app.db.query_optimizer import QueryOptimizer

    if not records:
        return 0

    # 分块插入（每次1000条）
    inserted = 0
    for chunk in ChunkedIterator(records, chunk_size=1000):
        inserted += QueryOptimizer.batch_insert(table, chunk)

    return inserted


# 进度追踪

class ProgressTracker:
    """进度追踪器"""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = datetime.now()

    def update(self, success: bool = True):
        """更新进度"""
        if success:
            self.completed += 1
        else:
            self.failed += 1

    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        processed = self.completed + self.failed
        percentage = (processed / self.total * 100) if self.total > 0 else 0

        # 估算剩余时间
        if processed > 0:
            avg_time = elapsed / processed
            remaining = (self.total - processed) * avg_time
        else:
            remaining = 0

        return {
            'total': self.total,
            'completed': self.completed,
            'failed': self.failed,
            'processed': processed,
            'percentage': round(percentage, 2),
            'elapsed_seconds': round(elapsed, 2),
            'estimated_remaining_seconds': round(remaining, 2)
        }


# 全局批量处理器实例
batch_processor = BatchProcessor(max_workers=10)
