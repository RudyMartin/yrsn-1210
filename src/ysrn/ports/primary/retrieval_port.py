"""Context retrieval port interface."""

from abc import ABC, abstractmethod
from typing import List, Dict
from ...domain.model import Query, ContextBlock


class ContextRetrievalPort(ABC):
    """Port for context retrieval operations."""
    
    @abstractmethod
    async def retrieve_context(self, query: Query, 
                               top_k: int = 10) -> List[ContextBlock]:
        """Retrieve relevant context blocks."""
        pass
    
    @abstractmethod
    async def rank_results(self, query: Query,
                          candidates: List[ContextBlock]) -> List[ContextBlock]:
        """Re-rank candidate context blocks."""
        pass
    
    @abstractmethod
    async def classify_context(self, context: ContextBlock, 
                              query: Query) -> Dict:
        """Classify context as R/S/N with scores."""
        pass


