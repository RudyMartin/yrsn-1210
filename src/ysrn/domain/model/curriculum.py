"""Curriculum domain models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class CurriculumStage:
    """A stage in the curriculum."""
    stage_number: int
    name: str
    description: str
    active_constraints: List[str] = field(default_factory=list)
    difficulty_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningProgress:
    """Learning progress tracking."""
    current_stage: int
    accuracy_history: List[float] = field(default_factory=list)
    solve_time_history: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_result(self, accuracy: float, solve_time: float) -> None:
        """Add a learning result."""
        self.accuracy_history.append(accuracy)
        self.solve_time_history.append(solve_time)
        self.last_updated = datetime.utcnow()
    
    def should_advance(self, threshold_accuracy: float = 0.9, 
                      threshold_time: float = 5.0) -> bool:
        """Check if should advance to next stage."""
        if len(self.accuracy_history) < 10:
            return False
        
        recent_accuracy = sum(self.accuracy_history[-10:]) / 10
        recent_time = sum(self.solve_time_history[-10:]) / 10
        
        return recent_accuracy >= threshold_accuracy and recent_time <= threshold_time


