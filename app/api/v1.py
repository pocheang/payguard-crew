"""
API v1 router - groups all v1 endpoints
"""
from fastapi import APIRouter

from app.api.audit import router as audit_router
from app.api.health import router as health_router
from app.api.metrics import router as metrics_router

# Create v1 router
api_v1_router = APIRouter(prefix="/api/v1")

# Include all v1 routes
api_v1_router.include_router(audit_router, prefix="/audit", tags=["audit"])
api_v1_router.include_router(health_router, prefix="/health", tags=["health"])
api_v1_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])

# Backward compatibility - keep routes at root level too
legacy_router = APIRouter()
legacy_router.include_router(audit_router, prefix="/audit", tags=["audit"])
legacy_router.include_router(health_router, tags=["health"])
legacy_router.include_router(metrics_router, tags=["metrics"])
