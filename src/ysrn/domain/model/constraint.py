"""Constraint domain models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..value_object.weight import ConstraintWeight


@dataclass
class Constraint:
    """A constraint in the system."""
    type: str
    weight: float
    source: str = "memristor"  # "memristor", "sensor", "human", "manual"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_weight(self) -> ConstraintWeight:
        return ConstraintWeight(
            value=self.weight,
            constraint_type=self.type,
            source=self.source
        )


@dataclass
class ConstraintSet:
    """A collection of constraints."""
    constraints: List[Constraint] = field(default_factory=list)
    
    def get_weight(self, constraint_type: str) -> float:
        """Get weight for constraint type."""
        for c in self.constraints:
            if c.type == constraint_type:
                return c.weight
        return 0.0
    
    def add(self, constraint: Constraint) -> None:
        """Add a constraint."""
        # Replace if exists
        self.constraints = [c for c in self.constraints if c.type != constraint.type]
        self.constraints.append(constraint)


