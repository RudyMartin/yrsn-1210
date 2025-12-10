"""Health check infrastructure."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a component."""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict = None
    last_checked: Optional[datetime] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.last_checked is None:
            self.last_checked = datetime.utcnow()


class HealthChecker:
    """Manages health checks for system components."""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.checkers: Dict[str, callable] = {}
    
    def register_component(self, name: str, checker: callable) -> None:
        """Register a health check function for a component."""
        self.checkers[name] = checker
    
    async def check_component(self, name: str) -> ComponentHealth:
        """Check health of a specific component."""
        if name not in self.checkers:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="No health checker registered"
            )
        
        try:
            checker = self.checkers[name]
            if asyncio.iscoroutinefunction(checker):
                result = await checker()
            else:
                result = checker()
            
            if isinstance(result, ComponentHealth):
                health = result
            elif isinstance(result, dict):
                health = ComponentHealth(
                    name=name,
                    status=HealthStatus(result.get("status", "unknown")),
                    message=result.get("message", ""),
                    details=result.get("details", {})
                )
            else:
                health = ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                )
            
            health.last_checked = datetime.utcnow()
            self.components[name] = health
            return health
        except Exception as e:
            health = ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
            health.last_checked = datetime.utcnow()
            self.components[name] = health
            return health
    
    async def check_all(self) -> Dict[str, ComponentHealth]:
        """Check health of all registered components."""
        tasks = [self.check_component(name) for name in self.checkers.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.checkers.keys(), results):
            if isinstance(result, Exception):
                self.components[name] = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Exception: {str(result)}"
                )
        
        return self.components
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.components:
            return HealthStatus.UNKNOWN
        
        statuses = [comp.status for comp in self.components.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_summary(self) -> Dict:
        """Get health check summary."""
        overall = self.get_overall_status()
        return {
            "status": overall.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                name: {
                    "status": comp.status.value,
                    "message": comp.message,
                    "details": comp.details,
                    "last_checked": comp.last_checked.isoformat() if comp.last_checked else None
                }
                for name, comp in self.components.items()
            }
        }


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


