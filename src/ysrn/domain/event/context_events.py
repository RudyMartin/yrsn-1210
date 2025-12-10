"""Context-related domain events."""

from dataclasses import dataclass, field
from typing import List
import uuid
from datetime import datetime


@dataclass
class DomainEvent:
    """Base class for domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "domain_event"


@dataclass
class ContextRetrievedEvent(DomainEvent):
    """Fired when context is retrieved."""
    query_id: str = ""
    context_ids: List[str] = field(default_factory=list)
    event_type: str = "context_retrieved"


@dataclass
class ContextClassifiedEvent(DomainEvent):
    """Fired when context is classified as R/S/N."""
    context_id: str = ""
    relevance: float = 0.0
    superfluous: float = 0.0
    noise: float = 0.0
    event_type: str = "context_classified"


@dataclass
class ContextRankedEvent(DomainEvent):
    """Fired when contexts are ranked."""
    query_id: str = ""
    ranked_context_ids: List[str] = field(default_factory=list)
    scores: List[float] = field(default_factory=list)
    event_type: str = "context_ranked"


