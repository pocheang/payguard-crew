"""
风险检测Agent的JSON Schema定义

包含：Fraud Detection, Merchant Risk, Device Fingerprint, Velocity Check
"""

RISK_AGENT_SCHEMAS = {
    "fraud_detection_agent": {
        "type": "object",
        "required": ["fraud_indicators", "anomaly_score", "fraud_type", "confidence"],
        "properties": {
            "fraud_indicators": {
                "type": "array",
                "items": {"type": "string"}
            },
            "anomaly_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
            },
            "fraud_type": {
                "type": "string",
                "enum": ["clean", "suspicious", "account_takeover", "card_testing", "velocity_abuse"]
            },
            "confidence": {
                "type": "string",
                "enum": ["low", "medium", "high"]
            }
        }
    },

    "merchant_risk_agent": {
        "type": "object",
        "required": ["merchant_risk_factors", "merchant_reputation_score", "high_risk_category", "recommendation"],
        "properties": {
            "merchant_risk_factors": {
                "type": "array",
                "items": {"type": "string"}
            },
            "merchant_reputation_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
            },
            "high_risk_category": {
                "type": "boolean"
            },
            "recommendation": {
                "type": "string"
            }
        }
    },

    "device_fingerprint_agent": {
        "type": "object",
        "required": ["device_risk_signals", "device_trust_score", "is_emulator", "is_vpn_proxy", "device_reputation"],
        "properties": {
            "device_risk_signals": {
                "type": "array",
                "items": {"type": "string"}
            },
            "device_trust_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
            },
            "is_emulator": {
                "type": "boolean"
            },
            "is_vpn_proxy": {
                "type": "boolean"
            },
            "device_reputation": {
                "type": "string",
                "enum": ["trusted", "neutral", "suspicious", "malicious"]
            }
        }
    },

    "velocity_check_agent": {
        "type": "object",
        "required": ["velocity_violations", "velocity_risk_score", "burst_detected", "time_pattern_anomaly", "recommendation"],
        "properties": {
            "velocity_violations": {
                "type": "array",
                "items": {"type": "string"}
            },
            "velocity_risk_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
            },
            "burst_detected": {
                "type": "boolean"
            },
            "time_pattern_anomaly": {
                "type": "boolean"
            },
            "recommendation": {
                "type": "string"
            }
        }
    }
}
