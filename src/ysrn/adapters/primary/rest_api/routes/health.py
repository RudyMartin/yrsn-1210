"""Health and metrics endpoints."""

from fastapi import APIRouter, Response
from datetime import datetime
from ..models import HealthResponse
from ysrn import __version__
from ysrn.infrastructure.health import get_health_checker
from ysrn.infrastructure.metrics import get_metrics, initialize_metrics


router = APIRouter(tags=["health"])

# Initialize metrics on module load
initialize_metrics()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and all components.
    """
    health_checker = get_health_checker()
    summary = await health_checker.check_all()
    
    overall_status = health_checker.get_overall_status()
    
    return {
        "status": overall_status.value,
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            name: {
                "status": comp.status.value,
                "message": comp.message,
                "last_checked": comp.last_checked.isoformat() if comp.last_checked else None
            }
            for name, comp in summary.items()
        }
    }


@router.get("/health/live")
async def liveness():
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if the service is ready to accept traffic.
    """
    health_checker = get_health_checker()
    await health_checker.check_all()
    overall_status = health_checker.get_overall_status()
    
    if overall_status.value == "healthy":
        return {"status": "ready"}
    else:
        return Response(
            content='{"status": "not ready"}',
            status_code=503,
            media_type="application/json"
        )


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format.
    """
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4"
    )

