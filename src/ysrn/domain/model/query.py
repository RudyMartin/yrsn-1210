"""Query domain models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..value_object.embedding import QueryEmbedding
from .context import ContextBlock


@dataclass
class Query:
    """A query for context retrieval."""
    id: str
    text: str
    embedding: Optional[QueryEmbedding] = None
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryResult:
    """Result of a query."""
    query_id: str
    contexts: List[ContextBlock]
    total_candidates: int
    processing_time_ms: float
    decomposition_stats: Dict[str, float] = field(default_factory=dict)
    
    @property
    def top_context(self) -> Optional[ContextBlock]:
        return self.contexts[0] if self.contexts else None


