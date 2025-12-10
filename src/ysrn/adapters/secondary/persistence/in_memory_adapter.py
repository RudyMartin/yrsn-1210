"""In-memory persistence adapter for testing."""

from typing import Dict, List, Optional
import numpy as np
import uuid
from ....ports.secondary.persistence_port import PersistencePort
from ....domain.model import ContextBlock


class InMemoryPersistenceAdapter(PersistencePort):
    """In-memory persistence for testing."""
    
    def __init__(self):
        self.contexts: Dict[str, ContextBlock] = {}
        self.checkpoints: Dict[str, Dict] = {}
    
    async def save_context(self, context: ContextBlock) -> None:
        self.contexts[context.id] = context
    
    async def load_context(self, context_id: str) -> Optional[ContextBlock]:
        return self.contexts.get(context_id)
    
    async def search_similar(self, embedding: np.ndarray,
                            top_k: int) -> List[ContextBlock]:
        if not self.contexts:
            return []
        
        # Simple cosine similarity search
        scores = []
        for ctx in self.contexts.values():
            if ctx.embedding:
                ctx_vec = ctx.embedding.to_numpy()
                sim = np.dot(embedding, ctx_vec) / (
                    np.linalg.norm(embedding) * np.linalg.norm(ctx_vec) + 1e-8
                )
                scores.append((ctx, sim))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return [ctx for ctx, _ in scores[:top_k]]
    
    async def save_checkpoint(self, state: Dict) -> str:
        checkpoint_id = str(uuid.uuid4())
        self.checkpoints[checkpoint_id] = state
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        return self.checkpoints.get(checkpoint_id)


