"""ChromaDB persistence adapter for vector storage."""

from typing import Dict, List, Optional
import numpy as np
import uuid
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from ....ports.secondary.persistence_port import PersistencePort
from ....domain.model import ContextBlock
from ....domain.value_object.embedding import ContextEmbedding


class ChromaDBPersistenceAdapter(PersistencePort):
    """ChromaDB adapter for vector persistence."""
    
    def __init__(self,
                 collection_name: str = "ysrn_contexts",
                 persist_directory: Optional[str] = "./chroma_db",
                 host: Optional[str] = None,
                 port: Optional[int] = None):
        """
        Initialize ChromaDB adapter.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Local directory for persistence (None for in-memory)
            host: ChromaDB server host (None for local)
            port: ChromaDB server port (None for local)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install with: pip install chromadb"
            )
        
        # Initialize ChromaDB client
        if host and port:
            # Remote ChromaDB server
            self.client = chromadb.HttpClient(host=host, port=port)
        elif persist_directory:
            # Local persistent ChromaDB
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            # In-memory ChromaDB
            self.client = chromadb.Client(
                settings=Settings(anonymized_telemetry=False)
            )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Metadata storage (for non-vector data)
        self.metadata_cache: Dict[str, Dict] = {}
    
    def _serialize_context(self, context: ContextBlock) -> Dict:
        """Serialize context metadata."""
        return {
            'id': context.id,
            'content': context.content,
            'metadata': context.metadata,
            'created_at': context.created_at.isoformat(),
            'relevance_score': context.relevance_score,
            'superfluous_score': context.superfluous_score,
            'noise_score': context.noise_score,
        }
    
    def _deserialize_context(self, data: Dict, embedding: Optional[np.ndarray] = None) -> ContextBlock:
        """Deserialize context from metadata and embedding."""
        context_embedding = None
        if embedding is not None:
            context_embedding = ContextEmbedding.from_numpy(embedding)
        
        return ContextBlock(
            id=data['id'],
            content=data['content'],
            embedding=context_embedding,
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat())),
            relevance_score=data.get('relevance_score'),
            superfluous_score=data.get('superfluous_score'),
            noise_score=data.get('noise_score')
        )
    
    async def save_context(self, context: ContextBlock) -> None:
        """Save context to ChromaDB."""
        if context.embedding is None:
            raise ValueError("Context must have an embedding to save to ChromaDB")
        
        embedding = context.embedding.to_numpy()
        metadata = self._serialize_context(context)
        
        # Store in ChromaDB
        self.collection.add(
            ids=[context.id],
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
            documents=[context.content]  # Store content as document
        )
        
        # Cache metadata
        self.metadata_cache[context.id] = metadata
    
    async def load_context(self, context_id: str) -> Optional[ContextBlock]:
        """Load context from ChromaDB."""
        try:
            results = self.collection.get(
                ids=[context_id],
                include=['embeddings', 'metadatas', 'documents']
            )
            
            if not results['ids']:
                return None
            
            # Get first result
            idx = 0
            metadata = results['metadatas'][idx]
            embedding_list = results['embeddings'][idx]
            content = results['documents'][idx]
            
            embedding = np.array(embedding_list)
            
            # Update metadata with content
            metadata['content'] = content
            
            return self._deserialize_context(metadata, embedding)
        except Exception as e:
            print(f"Warning: Failed to load context {context_id}: {e}")
            return None
    
    async def search_similar(self, embedding: np.ndarray,
                            top_k: int) -> List[ContextBlock]:
        """Search for similar contexts using ChromaDB."""
        try:
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=top_k,
                include=['embeddings', 'metadatas', 'documents', 'distances']
            )
            
            contexts = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    embedding_list = results['embeddings'][0][i]
                    content = results['documents'][0][i]
                    
                    embedding = np.array(embedding_list)
                    metadata['content'] = content
                    
                    context = self._deserialize_context(metadata, embedding)
                    contexts.append(context)
            
            return contexts
        except Exception as e:
            print(f"Warning: ChromaDB search failed: {e}")
            return []
    
    async def save_checkpoint(self, state: Dict) -> str:
        """Save checkpoint (store as metadata in ChromaDB)."""
        checkpoint_id = str(uuid.uuid4())
        
        # Store checkpoint in a separate collection
        checkpoint_collection = self.client.get_or_create_collection(
            name="ysrn_checkpoints"
        )
        
        checkpoint_collection.add(
            ids=[checkpoint_id],
            embeddings=[[0.0]],  # Dummy embedding
            metadatas=[state],
            documents=[str(state)]
        )
        
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Load checkpoint from ChromaDB."""
        try:
            checkpoint_collection = self.client.get_or_create_collection(
                name="ysrn_checkpoints"
            )
            
            results = checkpoint_collection.get(
                ids=[checkpoint_id],
                include=['metadatas']
            )
            
            if results['ids']:
                return results['metadatas'][0]
            return None
        except Exception as e:
            print(f"Warning: Failed to load checkpoint {checkpoint_id}: {e}")
            return None


