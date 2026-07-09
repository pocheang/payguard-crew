"""
Agent JSON Schema 定义

将9个Agent的Schema分离到独立文件，便于维护和扩展
"""
from app.crew.schemas.core_agents import CORE_AGENT_SCHEMAS
from app.crew.schemas.risk_agents import RISK_AGENT_SCHEMAS

# 合并所有Schema
AGENT_SCHEMAS = {
    **CORE_AGENT_SCHEMAS,
    **RISK_AGENT_SCHEMAS,
}

__all__ = ["AGENT_SCHEMAS"]
