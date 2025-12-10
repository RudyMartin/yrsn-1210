"""Context handler - Use case for context management."""

from typing import Dict, Optional
import uuid
from ..domain.model import ContextBlock
from ..domain.value_object.embedding import ContextEmbedding
from ..ports.secondary.encoder_port import EncoderPort
from ..ports.secondary.persistence_port import PersistencePort


class ContextHandler:
    """Handles context management use cases."""
    
    def __init__(self,
                 encoder: EncoderPort,
                 persistence: PersistencePort):
        
        self.encoder = encoder
        self.persistence = persistence
    
    async def add_context(self, content: str,
                         metadata: Dict = None) -> ContextBlock:
        """Add new context."""
        context_id = str(uuid.uuid4())
        embedding = await self.encoder.encode_context(content)
        
        context = ContextBlock(
            id=context_id,
            content=content,
            embedding=ContextEmbedding.from_numpy(embedding),
            metadata=metadata or {}
        )
        
        await self.persistence.save_context(context)
        return context
    
    async def get_context(self, context_id: str) -> Optional[ContextBlock]:
        """Get context by ID."""
        return await self.persistence.load_context(context_id)


