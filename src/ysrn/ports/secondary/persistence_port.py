"""Persistence port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import numpy as np
from ...domain.model import ContextBlock


class PersistencePort(ABC):
    """Port for data persistence."""
    
    @abstractmethod
    async def save_context(self, context: ContextBlock) -> None:
        """Save context."""
        pass
    
    @abstractmethod
    async def load_context(self, context_id: str) -> Optional[ContextBlock]:
        """Load context by ID."""
        pass
    
    @abstractmethod
    async def search_similar(self, embedding: np.ndarray,
                            top_k: int) -> List[ContextBlock]:
        """Search for similar contexts."""
        pass
    
    @abstractmethod
    async def save_checkpoint(self, state: Dict) -> str:
        """Save checkpoint, returns checkpoint_id."""
        pass
    
    @abstractmethod
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Load checkpoint."""
        pass


