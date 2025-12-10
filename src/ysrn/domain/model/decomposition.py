"""Decomposition domain models."""

from dataclasses import dataclass
import numpy as np


@dataclass
class DecompositionResult:
    """Result of Y=R+S+N decomposition."""
    Y: np.ndarray  # Original context tensor
    R: np.ndarray  # Relevant signal
    S: np.ndarray  # Superfluous content
    N: np.ndarray  # Noise
    
    relevance_ratio: float
    superfluous_ratio: float
    noise_ratio: float
    signal_quality: float  # R / (S + N)
    confidence: float
    
    # Per-component metadata
    r_components: int = 1
    s_components: int = 0
    n_components: int = 0


@dataclass
class TensorDecomposition:
    """Tensor decomposition representation."""
    result: DecompositionResult
    query_id: str
    context_id: str


@dataclass
class RSNComponents:
    """RSN component breakdown."""
    relevant: np.ndarray
    superfluous: np.ndarray
    noise: np.ndarray
    relevance_score: float
    noise_ratio: float
    signal_quality: float


