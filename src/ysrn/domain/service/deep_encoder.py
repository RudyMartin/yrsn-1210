"""
Deep Residual Encoder - From 1000-Layer paper insights

Key insight: Critical depth thresholds unlock emergent capabilities.
For context retrieval:
- Shallow (4-8 layers): Lexical matching
- Medium (32-64 layers): Structured retrieval
- Deep (256+ layers): Reasoning chains
"""

import numpy as np


class DeepResidualEncoder:
    """
    Deep encoder with residual connections.
    
    Architecture: [Dense → LayerNorm → Swish] × N layers
    
    From 1000-layer paper:
    - Depth enables richer contrastive representations
    - Critical thresholds for emergent behaviors
    - LayerNorm + Swish crucial for stability
    """
    
    def __init__(self,
                 input_dim: int = 768,
                 hidden_dim: int = 512,
                 output_dim: int = 512,
                 num_layers: int = 32,
                 use_layernorm: bool = True):
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.use_layernorm = use_layernorm
        
        # Initialize layers
        self.layers = []
        for i in range(num_layers):
            in_d = input_dim if i == 0 else hidden_dim
            out_d = output_dim if i == num_layers - 1 else hidden_dim
            
            layer = {
                'W': np.random.randn(in_d, out_d) * np.sqrt(2.0 / in_d),
                'b': np.zeros(out_d),
                'gamma': np.ones(out_d),
                'beta': np.zeros(out_d)
            }
            self.layers.append(layer)
        
        # Output projection
        self.W_out = np.random.randn(output_dim, output_dim) * 0.02
        
    def encode(self, x: np.ndarray) -> np.ndarray:
        """
        Encode input through deep residual network.
        """
        h = x
        
        for i, layer in enumerate(self.layers):
            # Linear transformation
            z = np.dot(h, layer['W']) + layer['b']
            
            # Layer normalization
            if self.use_layernorm:
                z = self._layer_norm(z, layer['gamma'], layer['beta'])
            
            # Swish activation
            z = self._swish(z)
            
            # Residual connection (when dimensions match)
            if i > 0 and h.shape == z.shape:
                z = z + h
            
            h = z
        
        # Output projection
        output = np.dot(h, self.W_out)
        
        return output
    
    def _layer_norm(self, x: np.ndarray, 
                   gamma: np.ndarray, 
                   beta: np.ndarray,
                   eps: float = 1e-5) -> np.ndarray:
        """Layer normalization."""
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + eps)
        return gamma * x_norm + beta
    
    def _swish(self, x: np.ndarray) -> np.ndarray:
        """Swish activation: x * sigmoid(x)"""
        return x * self._sigmoid(x)
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


