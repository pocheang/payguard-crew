"""
Base agent runner with common functionality
"""
from time import perf_counter
from typing import Any

from app.schemas.audit import AuditLogEntry
from app.schemas.transaction import TransactionInput
from app.crew.crewai_runner import run_crewai_json_task_async
from app.crew.utils import log_status


class BaseAgentRunner:
    """Base class for agent runners with common functionality"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
    
    async def run_agent(
        self,
        tx: TransactionInput,
        tx_payload: dict,
        registry: dict,
        attempted_crewai: bool,
        additional_context: dict | None = None,
        parser_func: Any = None,
        fallback_func: Any = None,
    ) -> tuple[dict, AuditLogEntry]:
        """
        Generic agent execution with timing, error handling, and logging
        
        Args:
            tx: Transaction input
            tx_payload: Transaction as dict
            registry: Agent registry
            attempted_crewai: Whether CrewAI was attempted
            additional_context: Extra context for agent (e.g., rule_result)
            parser_func: Function to parse CrewAI response
            fallback_func: Function to generate local fallback result
            
        Returns:
            Tuple of (agent_output, log_entry)
        """
        started = perf_counter()
        
        # Build input context
        input_context = {"transaction": tx_payload}
        if additional_context:
            input_context.update(additional_context)
        
        # Generate local fallback first
        local_result = fallback_func(tx, **additional_context) if additional_context else fallback_func(tx)
        
        # Try CrewAI if enabled
        agent_payload, llm_ms, error = await run_crewai_json_task_async(
            registry[self.agent_name],
            input_context,
        )
        
        # Parse CrewAI result
        parsed_result = parser_func(agent_payload) if parser_func and agent_payload else None
        if agent_payload and parsed_result is None and parser_func:
            error = error or f"CrewAI payload missing {self.agent_name} keys"
        
        # Build output
        agent_output = {
            "backend": "crewai" if parsed_result else "local",
            **(parsed_result or local_result),
        }
        
        # Create log entry
        log_entry = AuditLogEntry(
            agent_name=self.agent_name,
            input_data=str(input_context),
            output_data=str(agent_output),
            status=log_status(error, attempted_crewai),
            latency_ms=int((perf_counter() - started) * 1000) + llm_ms,
            error_message=error,
            created_at=None,
        )
        
        return agent_output, log_entry
