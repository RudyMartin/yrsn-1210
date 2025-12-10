"""Weight value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConstraintWeight:
    """Constraint weight from memristor state."""
    value: float  # [0, 1]
    constraint_type: str
    source: str = "memristor"  # or "manual", "sensor"


@dataclass(frozen=True)
class AttentionWeight:
    """Attention weight for gated retrieval."""
    value: float
    gate_score: float
    head_index: int = 0


