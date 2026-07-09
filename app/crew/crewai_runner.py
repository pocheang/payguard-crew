"""
CrewAI 任务执行器（异步优化版）
"""
import json
import asyncio
from time import perf_counter
from typing import Any

from app.agents.agent_factory import AgentSpec
from app.config import get_settings
from app.crew.utils import extract_json_object


JSONDict = dict[str, Any]


def run_crewai_json_task(
    spec: AgentSpec, context: JSONDict
) -> tuple[JSONDict | None, int, str | None]:
    """
    同步版本（保持向后兼容）
    """
    return asyncio.run(run_crewai_json_task_async(spec, context))


async def run_crewai_json_task_async(
    spec: AgentSpec, context: JSONDict, max_retries: int = 3
) -> tuple[JSONDict | None, int, str | None]:
    """
    异步执行 CrewAI JSON 任务（优化版）

    优化点：
    1. 支持异步执行
    2. 添加超时控制（5秒）
    3. 🔧 新增：重试机制（3次，指数退避）

    Args:
        spec: Agent规格
        context: 上下文数据
        max_retries: 最大重试次数（默认3次）

    Returns:
        (payload, latency_ms, error_message)
    """
    settings = get_settings()
    if not settings.enable_crewai:
        return None, 0, None
    if spec.instance is None:
        return None, 0, "CrewAI unavailable or LLM not configured"

    try:
        from crewai import Crew, Process, Task
    except ImportError:
        return None, 0, "CrewAI package not installed"

    started = perf_counter()
    last_error = None

    # 🔧 优化：重试机制（指数退避）
    for attempt in range(max_retries):
        try:
            # 超时时间：5秒 + 每次重试额外增加2秒
            timeout = 5.0 + (attempt * 2.0)

            result = await asyncio.wait_for(
                asyncio.to_thread(_run_crewai_task_sync, spec, context),
                timeout=timeout
            )

            payload = extract_json_object(result)
            latency_ms = int((perf_counter() - started) * 1000)

            if payload is None:
                last_error = "CrewAI returned invalid JSON"
                # JSON解析失败，重试
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))  # 指数退避：0.5s, 1s, 2s
                    continue
                return None, latency_ms, last_error

            # 成功
            return payload, latency_ms, None

        except asyncio.TimeoutError:
            latency_ms = int((perf_counter() - started) * 1000)
            last_error = f"CrewAI timeout after {timeout}s (attempt {attempt + 1}/{max_retries})"

            if attempt < max_retries - 1:
                # 重试前等待（指数退避）
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue

            return None, latency_ms, last_error

        except Exception as exc:
            latency_ms = int((perf_counter() - started) * 1000)
            last_error = f"{type(exc).__name__}: {exc}"

            # 某些异常不应重试（如配置错误）
            if "API key" in str(exc) or "authentication" in str(exc).lower():
                return None, latency_ms, last_error

            if attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue

            return None, latency_ms, last_error

    # 所有重试失败
    return None, int((perf_counter() - started) * 1000), last_error


def _run_crewai_task_sync(spec: AgentSpec, context: JSONDict) -> Any:
    """同步执行 CrewAI 任务的辅助函数"""
    from crewai import Crew, Process, Task

    task = Task(
        description=(
            f"{spec.prompt}\n"
            "Return strict JSON only.\n"
            f"Context: {json.dumps(context, ensure_ascii=False, default=str)}"
        ),
        expected_output=spec.expected_output,
        agent=spec.instance,
    )

    result = Crew(
        agents=[spec.instance],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    ).kickoff()

    return result
