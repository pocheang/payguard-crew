"""
核心Agent的JSON Schema定义

包含：Transaction, Risk Rule, Compliance, RAG Evidence, Report
"""

CORE_AGENT_SCHEMAS = {
    "transaction_agent": {
        "type": "object",
        "required": ["risk_points", "behavior_summary"],
        "properties": {
            "risk_points": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 0,
                "maxItems": 20
            },
            "behavior_summary": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1000
            }
        }
    },

    "risk_rule_agent": {
        "type": "object",
        "required": ["rule_explanation"],
        "properties": {
            "rule_explanation": {
                "type": "string",
                "minLength": 1,
                "maxLength": 2000
            }
        }
    },

    "compliance_agent": {
        "type": "object",
        "required": ["compliance_notes", "manual_review_reason"],
        "properties": {
            "compliance_notes": {
                "type": "array",
                "items": {"type": "string"}
            },
            "manual_review_reason": {
                "type": "string"
            }
        }
    },

    "rag_evidence_agent": {
        "type": "object",
        "required": ["evidence_summary"],
        "properties": {
            "evidence_summary": {
                "type": "string",
                "maxLength": 2000
            }
        }
    },

    "report_agent": {
        "type": "object",
        "required": ["summary", "suggestion"],
        "properties": {
            "summary": {
                "type": "string",
                "minLength": 10,
                "maxLength": 5000
            },
            "suggestion": {
                "type": "string",
                "minLength": 10,
                "maxLength": 1000
            }
        }
    }
}
