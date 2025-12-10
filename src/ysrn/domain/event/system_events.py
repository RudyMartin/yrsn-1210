"""System-related domain events."""

from dataclasses import dataclass, field
from .context_events import DomainEvent


@dataclass
class HealthChangedEvent(DomainEvent):
    """Fired when system health changes."""
    component: str = ""
    status: str = "healthy"  # "healthy", "degraded", "unhealthy"
    event_type: str = "health_changed"


@dataclass
class ThresholdBreachedEvent(DomainEvent):
    """Fired when a threshold is breached."""
    metric_name: str = ""
    threshold_value: float = 0.0
    actual_value: float = 0.0
    event_type: str = "threshold_breached"


