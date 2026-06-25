"""
Fallbacks package - Modular fallback logic
"""
from app.crew.fallbacks.core_fallbacks import (
    build_transaction_findings,
    build_compliance_notes,
    build_fallback_summary,
    build_fallback_suggestion,
)
from app.crew.fallbacks.risk_fallbacks import (
    build_fraud_detection_result,
    build_merchant_risk_result,
    build_device_fingerprint_result,
    build_velocity_check_result,
)

__all__ = [
    # Core fallbacks
    "build_transaction_findings",
    "build_compliance_notes",
    "build_fallback_summary",
    "build_fallback_suggestion",
    # Risk detection fallbacks
    "build_fraud_detection_result",
    "build_merchant_risk_result",
    "build_device_fingerprint_result",
    "build_velocity_check_result",
]
