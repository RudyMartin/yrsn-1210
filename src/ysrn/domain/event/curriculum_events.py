"""Curriculum-related domain events."""

from dataclasses import dataclass, field
from .context_events import DomainEvent


@dataclass
class StageAdvancedEvent(DomainEvent):
    """Fired when curriculum stage advances."""
    old_stage: int = 0
    new_stage: int = 0
    trigger: str = ""
    event_type: str = "curriculum_advanced"


@dataclass
class ConstraintUpdatedEvent(DomainEvent):
    """Fired when constraint weight updates."""
    constraint_type: str = ""
    old_weight: float = 0.0
    new_weight: float = 0.0
    source: str = ""  # "memristor", "sensor", "human"
    event_type: str = "constraint_updated"


