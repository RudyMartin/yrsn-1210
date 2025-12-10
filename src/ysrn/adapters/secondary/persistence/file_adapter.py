"""File-based persistence adapter for local development."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import uuid
from datetime import datetime

from ....ports.secondary.persistence_port import PersistencePort
from ....domain.model import ContextBlock
from ....domain.value_object.embedding import ContextEmbedding


class FilePersistenceAdapter(PersistencePort):
    """File-based persistence using JSON files."""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize file-based persistence.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.contexts_file = self.data_dir / "contexts.jsonl"
        self.checkpoints_dir = self.data_dir / "checkpoints"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for contexts (loaded on init)
        self._contexts_cache: Dict[str, ContextBlock] = {}
        self._load_contexts()
    
    def _load_contexts(self) -> None:
        """Load contexts from file into cache."""
        if not self.contexts_file.exists():
            return
        
        try:
            with open(self.contexts_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        context = self._deserialize_context(data)
                        self._contexts_cache[context.id] = context
        except Exception as e:
            print(f"Warning: Failed to load contexts: {e}")
    
    def _serialize_context(self, context: ContextBlock) -> Dict:
        """Serialize context to dict."""
        data = {
            'id': context.id,
            'content': context.content,
            'metadata': context.metadata,
            'created_at': context.created_at.isoformat(),
            'relevance_score': context.relevance_score,
            'superfluous_score': context.superfluous_score,
            'noise_score': context.noise_score,
        }
        
        if context.embedding:
            data['embedding'] = {
                'vector': context.embedding.vector,
                'dimension': context.embedding.dimension,
                'model_id': context.embedding.model_id
            }
        
        return data
    
    def _deserialize_context(self, data: Dict) -> ContextBlock:
        """Deserialize context from dict."""
        embedding = None
        if 'embedding' in data and data['embedding']:
            emb_data = data['embedding']
            embedding = ContextEmbedding(
                vector=tuple(emb_data['vector']),
                dimension=emb_data['dimension'],
                model_id=emb_data.get('model_id', 'default')
            )
        
        return ContextBlock(
            id=data['id'],
            content=data['content'],
            embedding=embedding,
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat())),
            relevance_score=data.get('relevance_score'),
            superfluous_score=data.get('superfluous_score'),
            noise_score=data.get('noise_score')
        )
    
    async def save_context(self, context: ContextBlock) -> None:
        """Save context to file (append mode)."""
        # Update cache
        self._contexts_cache[context.id] = context
        
        # Append to file
        data = self._serialize_context(context)
        with open(self.contexts_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    async def load_context(self, context_id: str) -> Optional[ContextBlock]:
        """Load context from cache."""
        return self._contexts_cache.get(context_id)
    
    async def search_similar(self, embedding: np.ndarray,
                            top_k: int) -> List[ContextBlock]:
        """Search for similar contexts using cosine similarity."""
        if not self._contexts_cache:
            return []
        
        # Compute cosine similarity
        scores = []
        for ctx in self._contexts_cache.values():
            if ctx.embedding:
                ctx_vec = ctx.embedding.to_numpy()
                # Cosine similarity
                dot_product = np.dot(embedding, ctx_vec)
                norm_product = np.linalg.norm(embedding) * np.linalg.norm(ctx_vec)
                sim = dot_product / (norm_product + 1e-8)
                scores.append((ctx, sim))
        
        # Sort by similarity and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [ctx for ctx, _ in scores[:top_k]]
    
    async def save_checkpoint(self, state: Dict) -> str:
        """Save checkpoint to file."""
        checkpoint_id = str(uuid.uuid4())
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Load checkpoint from file."""
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load checkpoint {checkpoint_id}: {e}")
            return None


