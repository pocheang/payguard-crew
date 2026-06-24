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
    spec: AgentSpec, context: JSONDict
) -> tuple[JSONDict | None, int, str | None]:
    """
    异步执行 CrewAI JSON 任务（优化版）

    优化点：
    1. 支持异步执行
    2. 添加超时控制（5秒）

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

    try:
        # 🚀 优化点：添加超时控制
        result = await asyncio.wait_for(
            asyncio.to_thread(_run_crewai_task_sync, spec, context),
            timeout=5.0  # 5秒超时
        )

        payload = extract_json_object(result)
        latency_ms = int((perf_counter() - started) * 1000)

        if payload is None:
            return None, latency_ms, "CrewAI returned invalid JSON"
        return payload, latency_ms, None

    except asyncio.TimeoutError:
        latency_ms = int((perf_counter() - started) * 1000)
        return None, latency_ms, "CrewAI timeout after 5s"
    except Exception as exc:
        latency_ms = int((perf_counter() - started) * 1000)
        return None, latency_ms, f"{type(exc).__name__}: {exc}"


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
