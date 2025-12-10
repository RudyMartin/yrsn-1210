"""Human feedback port interface."""

from abc import ABC, abstractmethod
from typing import Optional


class HumanFeedbackPort(ABC):
    """Port for human-in-the-loop feedback."""
    
    @abstractmethod
    async def submit_feedback(self, feedback_type: str,
                             constraint: Optional[str],
                             rating: Optional[float],
                             comment: str) -> None:
        """Submit human feedback."""
        pass
    
    @abstractmethod
    async def set_constraint_weight(self, constraint: str,
                                   weight: float) -> None:
        """Directly set constraint weight."""
        pass


