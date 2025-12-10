"""Sentence Transformers encoder adapter."""

from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from ....ports.secondary.encoder_port import EncoderPort


class SentenceTransformersEncoderAdapter(EncoderPort):
    """Encoder using Sentence Transformers library."""
    
    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 device: str = "cpu",
                 batch_size: int = 32):
        """
        Initialize Sentence Transformers encoder.
        
        Args:
            model_name: HuggingFace model name or path
            device: Device to run on ("cpu" or "cuda")
            batch_size: Batch size for encoding
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Sentence Transformers is not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        self.model_name = model_name
    
    async def encode_context(self, text: str) -> np.ndarray:
        """Encode context to embedding."""
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embedding
    
    async def encode_query(self, query: str) -> np.ndarray:
        """Encode query to embedding."""
        # Use same model for queries and contexts
        return await self.encode_context(query)
    
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Batch encode texts."""
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings


