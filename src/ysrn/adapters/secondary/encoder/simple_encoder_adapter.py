"""Simple encoder adapter using random projections (for testing)."""

from typing import List
import numpy as np
from ....ports.secondary.encoder_port import EncoderPort


class SimpleEncoderAdapter(EncoderPort):
    """Simple encoder using random projections (for testing)."""
    
    def __init__(self, output_dim: int = 512):
        self.output_dim = output_dim
        # Simple hash-based projection (placeholder for real encoder)
        np.random.seed(42)
        self.projection = np.random.randn(10000, output_dim) * 0.01
    
    async def encode_context(self, text: str) -> np.ndarray:
        return await self._encode(text)
    
    async def encode_query(self, query: str) -> np.ndarray:
        return await self._encode(query)
    
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        embeddings = [await self._encode(t) for t in texts]
        return np.stack(embeddings)
    
    async def _encode(self, text: str) -> np.ndarray:
        # Simple bag-of-words style encoding
        tokens = text.lower().split()
        embedding = np.zeros(self.output_dim)
        
        for token in tokens:
            token_hash = hash(token) % 10000
            embedding += self.projection[token_hash]
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm
        
        return embedding


