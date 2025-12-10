"""Encoder port interface."""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class EncoderPort(ABC):
    """Port for deep encoding (embeddings)."""
    
    @abstractmethod
    async def encode_context(self, text: str) -> np.ndarray:
        """Encode context to embedding."""
        pass
    
    @abstractmethod
    async def encode_query(self, query: str) -> np.ndarray:
        """Encode query to embedding."""
        pass
    
    @abstractmethod
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Batch encode texts."""
        pass


