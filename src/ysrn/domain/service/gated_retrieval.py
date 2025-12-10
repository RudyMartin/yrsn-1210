"""
Gated Context Retrieval - From Gated Attention paper

Key insight: Apply sigmoid gate after SDPA to:
1. Break low-rank bottleneck
2. Enable query-dependent sparse filtering
3. Eliminate attention sinks
"""

import numpy as np
from typing import List, Tuple
from ..model.context import ContextBlock
from ..model.query import Query


class GatedContextRetriever:
    """
    Implements gated attention for context retrieval.
    
    From Gated Attention paper:
    - Gate position G1 (after SDPA) is most effective
    - Head-specific gates crucial
    - Mean gate score ~0.116 (90% suppression) is optimal
    """
    
    def __init__(self,
                 num_heads: int = 8,
                 head_dim: int = 64,
                 gate_init_bias: float = -2.0):  # Bias toward sparsity
        
        self.num_heads = num_heads
        self.head_dim = head_dim
        hidden_dim = num_heads * head_dim
        
        # Gate projection (would be learned)
        self.W_gate = np.random.randn(hidden_dim, hidden_dim) * 0.02
        self.gate_bias = np.full(hidden_dim, gate_init_bias)
        
    def compute_gated_attention(self,
                                query: np.ndarray,
                                keys: np.ndarray,
                                values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute gated attention.
        
        Y' = Y ⊙ σ(X @ W_gate + b)
        
        where Y is SDPA output, σ is sigmoid
        """
        # Standard SDPA
        d_k = query.shape[-1]
        scores = np.dot(query, keys.T) / np.sqrt(d_k + 1e-8)
        attention_weights = self._softmax(scores)
        sdpa_output = np.dot(attention_weights, values)
        
        # Compute gate (query-dependent)
        gate_logits = np.dot(query, self.W_gate) + self.gate_bias
        gate = self._sigmoid(gate_logits)
        
        # Apply gate (element-wise)
        if len(gate) >= len(sdpa_output):
            gated_output = sdpa_output * gate[:len(sdpa_output)]
        else:
            gated_output = sdpa_output * np.resize(gate, len(sdpa_output))
        
        return gated_output, gate
    
    def retrieve(self,
                query: Query,
                candidates: List[ContextBlock],
                top_k: int = 10) -> List[ContextBlock]:
        """
        Retrieve top-k contexts using gated attention.
        """
        if not candidates or query.embedding is None:
            return []
        
        q_vec = query.embedding.to_numpy()
        
        # Get embeddings for candidates
        valid_candidates = [c for c in candidates if c.embedding is not None]
        if not valid_candidates:
            return []
        
        keys = np.stack([c.embedding.to_numpy() for c in valid_candidates])
        values = keys
        
        # Compute gated attention
        gated_out, gates = self.compute_gated_attention(q_vec, keys, values)
        
        # Compute final scores
        relevance = np.dot(q_vec, keys.T)
        mean_gate = np.mean(gates[:len(relevance)]) if len(gates) > 0 else 0.5
        final_scores = relevance * mean_gate
        
        # Sort and return top-k
        sorted_indices = np.argsort(final_scores)[::-1][:top_k]
        
        results = []
        for idx in sorted_indices:
            ctx = valid_candidates[idx]
            ctx.relevance_score = float(final_scores[idx])
            results.append(ctx)
        
        return results
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x))
        return exp_x / (exp_x.sum() + 1e-8)
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


