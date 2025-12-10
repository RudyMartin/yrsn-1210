"""OpenAI encoder adapter."""

from typing import List, Optional
import numpy as np

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ....ports.secondary.encoder_port import EncoderPort


class OpenAIEncoderAdapter(EncoderPort):
    """Encoder using OpenAI embeddings API."""
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "text-embedding-3-small",
                 organization: Optional[str] = None):
        """
        Initialize OpenAI encoder.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Embedding model to use
            organization: OpenAI organization ID (optional)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library is not installed. "
                "Install with: pip install openai"
            )
        
        self.client = OpenAI(api_key=api_key, organization=organization)
        self.model = model
    
    async def encode_context(self, text: str) -> np.ndarray:
        """Encode context to embedding."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return np.array(response.data[0].embedding)
    
    async def encode_query(self, query: str) -> np.ndarray:
        """Encode query to embedding."""
        return await self.encode_context(query)
    
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Batch encode texts."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        # Extract embeddings from response
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)


