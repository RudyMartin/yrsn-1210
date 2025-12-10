"""Query port interface."""

from abc import ABC, abstractmethod
from typing import Optional
from ...domain.model import Query, QueryResult


class QueryPort(ABC):
    """Port for submitting queries to YSRN."""
    
    @abstractmethod
    async def submit_query(self, query: Query) -> str:
        """Submit query, returns query_id."""
        pass
    
    @abstractmethod
    async def get_result(self, query_id: str, 
                        timeout: float = 30.0) -> Optional[QueryResult]:
        """Get query result."""
        pass
    
    @abstractmethod
    async def stream_results(self, query_id: str):
        """Stream incremental results."""
        pass


