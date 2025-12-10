"""
YSRN Core Engine - Y = R + S + N Decomposition

Implements semantic tensor decomposition to classify context into Relevant,
Superfluous, and Noise components.

Based on research synthesis:
- Tensor decomposition for semantic content classification
- R (Relevant): Signal that contributes to task
- S (Superfluous): Content that doesn't help or hurt
- N (Noise): Content that degrades performance

Mathematical Foundation:
Y = R + S + N where:
- Y is the full context tensor
- R is the relevant signal subspace
- S is the superfluous subspace (orthogonal to R)
- N is the noise component
"""

import numpy as np
from typing import List, Optional
from ..model.decomposition import DecompositionResult
from ..model.context import ContextBlock
from ..model.query import Query


class YSRNEngine:
    """
    Core YSRN decomposition engine.
    
    Implements semantic tensor decomposition to classify context
    into Relevant, Superfluous, and Noise components.
    """
    
    def __init__(self, 
                 relevance_threshold: float = 0.3,
                 noise_threshold: float = 0.1,
                 num_components: int = 64):
        
        self.relevance_threshold = relevance_threshold
        self.noise_threshold = noise_threshold
        self.num_components = num_components
        
        # Learned projection matrices (would be trained)
        self.W_relevance: Optional[np.ndarray] = None
        self.W_superfluous: Optional[np.ndarray] = None
        
    def decompose(self, 
                  context_embedding: np.ndarray,
                  query_embedding: np.ndarray) -> DecompositionResult:
        """
        Decompose context into R, S, N components relative to query.
        
        Algorithm:
        1. Project context onto query-aligned subspace (R candidate)
        2. Compute orthogonal complement (S + N candidate)
        3. Separate noise from superfluous using energy thresholds
        4. Apply learned refinement
        """
        # Normalize inputs
        Y = context_embedding / (np.linalg.norm(context_embedding) + 1e-8)
        q = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        # Step 1: Query-aligned projection (initial R estimate)
        # R_init = (Y · q) * q (projection onto query direction)
        relevance_coeff = np.dot(Y, q)
        R_init = relevance_coeff * q
        
        # Step 2: Orthogonal complement (S + N)
        residual = Y - R_init
        
        # Step 3: Separate noise using SVD
        # Low singular values → noise, mid → superfluous
        if len(residual.shape) == 1:
            residual = residual.reshape(-1, 1)
        
        try:
            U, s, Vt = np.linalg.svd(residual.reshape(-1, 1), full_matrices=False)
        except:
            # Fallback for numerical issues
            U, s, Vt = np.array([[1]]), np.array([np.linalg.norm(residual)]), np.array([[1]])
        
        # Threshold singular values
        total_energy = np.sum(s ** 2)
        cumulative_energy = np.cumsum(s ** 2) / (total_energy + 1e-8)
        
        # Noise: components below noise threshold
        noise_mask = cumulative_energy > (1 - self.noise_threshold)
        noise_indices = np.where(noise_mask)[0]
        
        # Reconstruct components
        if len(noise_indices) > 0:
            N = np.zeros_like(residual.flatten())
            for i in noise_indices:
                if i < len(s):
                    N += s[i] * U[:, i].flatten() * Vt[i, :].flatten() if Vt.shape[0] > i else 0
        else:
            N = np.zeros_like(residual.flatten())
        
        # S = residual - N
        S = residual.flatten() - N
        
        # Step 4: Refine R using learned projections (if available)
        if self.W_relevance is not None:
            R = self.W_relevance @ R_init
        else:
            R = R_init
        
        # Compute metrics
        Y_norm = np.linalg.norm(Y)
        R_norm = np.linalg.norm(R)
        S_norm = np.linalg.norm(S)
        N_norm = np.linalg.norm(N)
        
        total_norm = R_norm + S_norm + N_norm + 1e-8
        
        relevance_ratio = R_norm / total_norm
        noise_ratio = N_norm / total_norm
        superfluous_ratio = S_norm / total_norm
        signal_quality = R_norm / (S_norm + N_norm + 1e-8)
        
        return DecompositionResult(
            Y=Y,
            R=R,
            S=S,
            N=N,
            relevance_ratio=float(relevance_ratio),
            superfluous_ratio=float(superfluous_ratio),
            noise_ratio=float(noise_ratio),
            signal_quality=float(signal_quality),
            confidence=float(abs(relevance_coeff)),
            r_components=1,  # Simplified
            s_components=max(0, len(s) - len(noise_indices) - 1),
            n_components=len(noise_indices)
        )
    
    def batch_decompose(self, 
                       context_embeddings: np.ndarray,
                       query_embedding: np.ndarray) -> List[DecompositionResult]:
        """Decompose multiple contexts."""
        results = []
        for ctx in context_embeddings:
            results.append(self.decompose(ctx, query_embedding))
        return results
    
    def classify_context(self, 
                        context: ContextBlock,
                        query: Query) -> ContextBlock:
        """Classify context and update its RSN scores."""
        if context.embedding is None or query.embedding is None:
            raise ValueError("Both context and query must have embeddings")
        
        result = self.decompose(
            context.embedding.to_numpy(),
            query.embedding.to_numpy()
        )
        
        context.relevance_score = result.relevance_ratio
        context.superfluous_score = result.superfluous_ratio
        context.noise_score = result.noise_ratio
        
        return context
    
    def batch_classify(self,
                      contexts: List[ContextBlock],
                      query: Query) -> List[ContextBlock]:
        """Classify multiple contexts."""
        return [self.classify_context(ctx, query) for ctx in contexts]
    
    def train_projections(self, 
                         training_data: List,
                         labels: np.ndarray) -> None:
        """
        Train projection matrices from labeled data.
        
        training_data: List of (context, query, relevance_label) tuples
        """
        # This would implement the training loop
        # Using techniques from the research papers:
        # - Contrastive learning (1000-layer paper)
        # - Gated attention (Gated Attention paper)
        pass

