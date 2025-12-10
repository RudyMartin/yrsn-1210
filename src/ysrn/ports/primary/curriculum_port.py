"""Curriculum port interface."""

from abc import ABC, abstractmethod
from typing import List


class CurriculumPort(ABC):
    """Port for curriculum learning operations."""
    
    @abstractmethod
    async def get_current_stage(self) -> int:
        """Get current curriculum stage."""
        pass
    
    @abstractmethod
    async def evaluate_progression(self, 
                                   accuracy: float,
                                   solve_time: float) -> str:
        """Evaluate and potentially progress curriculum."""
        pass
    
    @abstractmethod
    async def get_active_constraints(self) -> List[str]:
        """Get currently active constraint types."""
        pass


