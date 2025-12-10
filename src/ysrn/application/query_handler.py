"""Query handler - Use case for query processing."""

from typing import List, Optional, Dict
import time
import uuid
import numpy as np
from ..domain.model import Query, QueryResult, ContextBlock
from ..domain.value_object.embedding import QueryEmbedding
from ..domain.service import YSRNEngine, GatedContextRetriever
from ..ports.secondary.encoder_port import EncoderPort
from ..ports.secondary.persistence_port import PersistencePort
from ..ports.secondary.event_bus_port import EventBusPort
from ..domain.event.context_events import ContextRetrievedEvent


class QueryHandler:
    """Handles query submission and retrieval use cases."""
    
    def __init__(self,
                 ysrn_engine: YSRNEngine,
                 retriever: GatedContextRetriever,
                 encoder: EncoderPort,
                 persistence: PersistencePort,
                 event_bus: EventBusPort):
        
        self.ysrn = ysrn_engine
        self.retriever = retriever
        self.encoder = encoder
        self.persistence = persistence
        self.event_bus = event_bus
        
        self.pending_queries: Dict[str, Query] = {}
        self.results: Dict[str, QueryResult] = {}
    
    async def submit_query(self, text: str,
                          constraints: List[str] = None) -> str:
        """Submit a new query."""
        start = time.perf_counter()
        
        # Create query
        query_id = str(uuid.uuid4())
        embedding = await self.encoder.encode_query(text)
        
        query = Query(
            id=query_id,
            text=text,
            embedding=QueryEmbedding.from_numpy(embedding),
            constraints=constraints or []
        )
        
        self.pending_queries[query_id] = query
        
        # Retrieve contexts
        candidates = await self.persistence.search_similar(embedding, top_k=50)
        
        # Apply gated retrieval
        results = self.retriever.retrieve(query, candidates, top_k=10)
        
        # Classify with YSRN
        classified = self.ysrn.batch_classify(results, query)
        
        # Sort by relevance
        classified.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        
        elapsed = (time.perf_counter() - start) * 1000
        
        # Store result
        result = QueryResult(
            query_id=query_id,
            contexts=classified,
            total_candidates=len(candidates),
            processing_time_ms=elapsed,
            decomposition_stats={
                'avg_relevance': float(np.mean([c.relevance_score or 0 for c in classified])),
                'avg_noise': float(np.mean([c.noise_score or 0 for c in classified]))
            }
        )
        
        self.results[query_id] = result
        
        # Publish event
        await self.event_bus.publish(ContextRetrievedEvent(
            query_id=query_id,
            context_ids=[c.id for c in classified]
        ))
        
        return query_id
    
    async def get_result(self, query_id: str,
                        timeout: float = 30.0) -> Optional[QueryResult]:
        """Get query result."""
        return self.results.get(query_id)


