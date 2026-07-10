"""
异步任务队列

基于Redis的轻量级任务队列：
- 后台任务执行
- 任务状态追踪
- 失败重试
- 优先级队列
"""
import json
import time
import threading
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from app.core.cache import cache


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    RETRY = "retry"          # 重试中


@dataclass
class Task:
    """任务"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    max_retries: int = 3
    retry_count: int = 0
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class TaskQueue:
    """任务队列管理器"""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.workers: list = []
        self.running = False

    def register_handler(self, task_type: str, handler: Callable):
        """
        注册任务处理器

        Args:
            task_type: 任务类型
            handler: 处理函数
        """
        self.handlers[task_type] = handler
        print(f"✓ Task handler registered: {task_type}")

    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        max_retries: int = 3
    ) -> str:
        """
        提交任务到队列

        Args:
            task_type: 任务类型
            payload: 任务数据
            priority: 优先级（1-10，数字越小优先级越高）
            max_retries: 最大重试次数

        Returns:
            任务ID
        """
        if not cache.enabled:
            # 如果Redis不可用，同步执行
            print(f"⚠ Redis disabled, executing task synchronously: {task_type}")
            return self._execute_synchronously(task_type, payload)

        task_id = f"task:{task_type}:{int(time.time() * 1000)}"

        task = Task(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries
        )

        # 保存任务到Redis
        task_key = f"payguard:task:{task_id}"
        cache.set(task_key, asdict(task), expire=86400)  # 24小时

        # 添加到优先级队列
        queue_key = f"payguard:queue:{task_type}"
        cache.client.zadd(queue_key, {task_id: priority})

        print(f"✓ Task submitted: {task_id}")
        return task_id

    def _execute_synchronously(self, task_type: str, payload: Dict[str, Any]) -> str:
        """同步执行任务（Redis不可用时的降级方案）"""
        handler = self.handlers.get(task_type)
        if not handler:
            raise ValueError(f"No handler for task type: {task_type}")

        try:
            result = handler(payload)
            return "sync_execution_success"
        except Exception as e:
            print(f"✗ Sync execution failed: {e}")
            raise

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        if not cache.enabled:
            return None

        task_key = f"payguard:task:{task_id}"
        task_data = cache.get(task_key)

        if task_data:
            return Task(**task_data)
        return None

    def start_workers(self, num_workers: int = 2):
        """
        启动后台工作线程

        Args:
            num_workers: 工作线程数
        """
        if not cache.enabled:
            print("⚠ Redis disabled, task workers not started")
            return

        self.running = True

        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            print(f"✓ Task worker {i} started")

    def stop_workers(self):
        """停止所有工作线程"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=5)
        self.workers.clear()
        print("✓ All task workers stopped")

    def _worker_loop(self, worker_id: int):
        """工作线程主循环"""
        while self.running:
            try:
                # 从所有队列中获取最高优先级任务
                task_id = self._fetch_next_task()

                if task_id:
                    self._execute_task(task_id, worker_id)
                else:
                    # 无任务时休眠
                    time.sleep(1)

            except Exception as e:
                print(f"✗ Worker {worker_id} error: {e}")
                time.sleep(1)

    def _fetch_next_task(self) -> Optional[str]:
        """获取下一个待执行任务"""
        if not cache.enabled:
            return None

        # 遍历所有任务类型队列
        for task_type in self.handlers.keys():
            queue_key = f"payguard:queue:{task_type}"

            # 使用ZPOPMIN获取最小优先级（最高优先级）任务
            try:
                result = cache.client.zpopmin(queue_key, 1)
                if result:
                    task_id = result[0][0].decode() if isinstance(result[0][0], bytes) else result[0][0]
                    return task_id
            except Exception as e:
                print(f"Fetch task error: {e}")

        return None

    def _execute_task(self, task_id: str, worker_id: int):
        """执行任务"""
        # 获取任务详情
        task_key = f"payguard:task:{task_id}"
        task_data = cache.get(task_key)

        if not task_data:
            print(f"✗ Task not found: {task_id}")
            return

        task = Task(**task_data)
        handler = self.handlers.get(task.task_type)

        if not handler:
            print(f"✗ No handler for task type: {task.task_type}")
            return

        # 更新任务状态为执行中
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        cache.set(task_key, asdict(task), expire=86400)

        print(f"Worker {worker_id} executing: {task_id}")

        try:
            # 执行任务
            result = handler(task.payload)

            # 标记完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
            cache.set(task_key, asdict(task), expire=86400)

            print(f"✓ Task completed: {task_id}")

        except Exception as e:
            print(f"✗ Task failed: {task_id}, error: {e}")

            # 处理失败
            task.error = str(e)
            task.retry_count += 1

            if task.retry_count < task.max_retries:
                # 重试
                task.status = TaskStatus.RETRY
                cache.set(task_key, asdict(task), expire=86400)

                # 重新入队（优先级降低）
                queue_key = f"payguard:queue:{task.task_type}"
                cache.client.zadd(queue_key, {task_id: task.priority + task.retry_count})

                print(f"⟲ Task will retry ({task.retry_count}/{task.max_retries}): {task_id}")
            else:
                # 标记为失败
                task.status = TaskStatus.FAILED
                cache.set(task_key, asdict(task), expire=86400)
                print(f"✗ Task failed permanently: {task_id}")


# 全局任务队列实例
task_queue = TaskQueue()


# 示例：注册批量审计任务处理器
def handle_batch_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """批量审计任务处理器"""
    from app.crew.audit_crew import run_audit_crew
    from app.schemas.transaction import TransactionInput

    transactions = payload.get('transactions', [])
    results = []

    for tx_data in transactions:
        try:
            tx = TransactionInput(**tx_data)
            result = run_audit_crew(tx)
            results.append({'transaction_id': tx.transaction_id, 'success': True, 'result': result})
        except Exception as e:
            results.append({'transaction_id': tx_data.get('transaction_id'), 'success': False, 'error': str(e)})

    return {
        'total': len(transactions),
        'success': sum(1 for r in results if r['success']),
        'results': results
    }


# 注册默认处理器
task_queue.register_handler('batch_audit', handle_batch_audit)
