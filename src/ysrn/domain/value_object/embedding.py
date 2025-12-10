"""Embedding value objects."""

from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class ContextEmbedding:
    """Immutable context embedding."""
    vector: Tuple[float, ...]
    dimension: int
    model_id: str = "default"
    
    @classmethod
    def from_numpy(cls, arr: np.ndarray, model_id: str = "default") -> 'ContextEmbedding':
        return cls(
            vector=tuple(arr.flatten().tolist()),
            dimension=arr.shape[-1],
            model_id=model_id
        )
    
    def to_numpy(self) -> np.ndarray:
        return np.array(self.vector)


@dataclass(frozen=True)
class QueryEmbedding:
    """Immutable query embedding."""
    vector: Tuple[float, ...]
    dimension: int
    
    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> 'QueryEmbedding':
        return cls(vector=tuple(arr.flatten().tolist()), dimension=arr.shape[-1])
    
    def to_numpy(self) -> np.ndarray:
        return np.array(self.vector)


