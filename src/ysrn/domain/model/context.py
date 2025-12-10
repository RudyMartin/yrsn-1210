"""Context domain models."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from ..value_object.embedding import ContextEmbedding


@dataclass
class ContextBlock:
    """A block of context content."""
    id: str
    content: str
    embedding: Optional[ContextEmbedding] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # RSN classification results
    relevance_score: Optional[float] = None
    superfluous_score: Optional[float] = None
    noise_score: Optional[float] = None
    
    def is_classified(self) -> bool:
        return self.relevance_score is not None


@dataclass
class ContextChunk:
    """A smaller chunk of context within a block."""
    id: str
    block_id: str
    content: str
    start_index: int
    end_index: int
    embedding: Optional[ContextEmbedding] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


