"""Feedback handler - Use case for human feedback."""

from typing import Optional, Dict
from ..domain.model.constraint import Constraint, ConstraintSet
from ..domain.value_object.weight import ConstraintWeight
from ..ports.secondary.persistence_port import PersistencePort
from ..ports.secondary.event_bus_port import EventBusPort
from ..domain.event.curriculum_events import ConstraintUpdatedEvent


class FeedbackHandler:
    """Handles human feedback use cases."""
    
    def __init__(self,
                 persistence: PersistencePort,
                 event_bus: EventBusPort):
        self.persistence = persistence
        self.event_bus = event_bus
        
        # In-memory constraint set (could be persisted)
        self.constraint_set = ConstraintSet()
        self._load_constraints()
    
    def _load_constraints(self) -> None:
        """Load constraints from persistence."""
        # For now, initialize with defaults
        # In production, load from persistence
        default_constraints = [
            Constraint(type="basic", weight=1.0, source="manual"),
            Constraint(type="moderate", weight=0.5, source="manual"),
            Constraint(type="advanced", weight=0.2, source="manual"),
        ]
        for c in default_constraints:
            self.constraint_set.add(c)
    
    async def submit_feedback(self,
                             feedback_type: str,
                             constraint: Optional[str],
                             rating: Optional[float],
                             comment: str) -> None:
        """
        Submit human feedback.
        
        Args:
            feedback_type: Type of feedback (e.g., "relevance", "quality")
            constraint: Optional constraint type this feedback relates to
            rating: Optional numeric rating (0.0 to 1.0)
            comment: Text comment
        """
        # Process feedback based on type
        if feedback_type == "constraint_weight" and constraint and rating is not None:
            # Update constraint weight based on feedback
            await self.set_constraint_weight(constraint, rating)
        elif feedback_type == "general":
            # Store general feedback (could be logged or stored)
            pass
        
        # Could publish feedback event here
        # await self.event_bus.publish(FeedbackSubmittedEvent(...))
    
    async def set_constraint_weight(self,
                                   constraint: str,
                                   weight: float) -> None:
        """
        Directly set constraint weight.
        
        Args:
            constraint: Constraint type
            weight: New weight value (0.0 to 1.0)
        """
        # Clamp weight to valid range
        weight = max(0.0, min(1.0, weight))
        
        # Get old weight before updating
        old_weight = self.constraint_set.get_weight(constraint)
        
        # Update constraint
        constraint_obj = Constraint(
            type=constraint,
            weight=weight,
            source="human"
        )
        self.constraint_set.add(constraint_obj)
        
        # Publish event
        await self.event_bus.publish(ConstraintUpdatedEvent(
            constraint_type=constraint,
            old_weight=old_weight,
            new_weight=weight,
            source="human_feedback"
        ))
        
        # Save to persistence
        await self._save_constraints()
    
    async def get_constraint_weight(self, constraint: str) -> float:
        """Get current weight for a constraint."""
        return self.constraint_set.get_weight(constraint)
    
    async def get_all_constraints(self) -> ConstraintSet:
        """Get all constraints."""
        return self.constraint_set
    
    async def _save_constraints(self) -> None:
        """Save constraints to persistence."""
        state = {
            'constraints': [
                {
                    'type': c.type,
                    'weight': c.weight,
                    'source': c.source,
                    'metadata': c.metadata
                }
                for c in self.constraint_set.constraints
            ]
        }
        await self.persistence.save_checkpoint(state)

