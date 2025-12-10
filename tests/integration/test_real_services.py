"""Integration tests using real services (not mocks)."""

import pytest
import numpy as np
from ysrn.domain.model import ContextBlock
from ysrn.domain.value_object.embedding import ContextEmbedding


@pytest.mark.integration
class TestRealSentenceTransformers:
    """Test real Sentence Transformers encoder."""
    
    @pytest.mark.asyncio
    async def test_encode_context(self, real_sentence_transformers_encoder):
        """Test encoding context with real Sentence Transformers."""
        text = "Machine learning is a subset of artificial intelligence."
        embedding = await real_sentence_transformers_encoder.encode_context(text)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 384  # all-MiniLM-L6-v2 dimension
        assert np.all(np.isfinite(embedding))
    
    @pytest.mark.asyncio
    async def test_encode_query(self, real_sentence_transformers_encoder):
        """Test encoding query with real Sentence Transformers."""
        query = "What is machine learning?"
        embedding = await real_sentence_transformers_encoder.encode_query(query)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 384
    
    @pytest.mark.asyncio
    async def test_encode_batch(self, real_sentence_transformers_encoder):
        """Test batch encoding with real Sentence Transformers."""
        texts = [
            "First text about machine learning.",
            "Second text about Python programming.",
            "Third text about FastAPI framework.",
        ]
        embeddings = await real_sentence_transformers_encoder.encode_batch(texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == 384


@pytest.mark.integration
@pytest.mark.requires_api
class TestRealOpenAI:
    """Test real OpenAI encoder (requires API key)."""
    
    @pytest.mark.asyncio
    async def test_encode_with_openai(self, real_openai_encoder):
        """Test encoding with real OpenAI API."""
        text = "Machine learning is a subset of artificial intelligence."
        embedding = await real_openai_encoder.encode_context(text)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == 1536  # text-embedding-3-small dimension
        assert np.all(np.isfinite(embedding))


@pytest.mark.integration
@pytest.mark.requires_db
class TestRealChromaDB:
    """Test real ChromaDB persistence."""
    
    @pytest.mark.asyncio
    async def test_save_and_load_context(self, real_chromadb_persistence, real_sentence_transformers_encoder):
        """Test saving and loading context with real ChromaDB."""
        # Create context
        text = "Machine learning is a subset of artificial intelligence."
        embedding = await real_sentence_transformers_encoder.encode_context(text)
        
        context = ContextBlock(
            id="test-1",
            content=text,
            embedding=ContextEmbedding.from_numpy(embedding),
            metadata={"source": "test"}
        )
        
        # Save
        await real_chromadb_persistence.save_context(context)
        
        # Load
        loaded = await real_chromadb_persistence.load_context("test-1")
        
        assert loaded is not None
        assert loaded.id == "test-1"
        assert loaded.content == text
        assert loaded.embedding is not None
    
    @pytest.mark.asyncio
    async def test_search_similar(self, real_chromadb_persistence, real_sentence_transformers_encoder):
        """Test similarity search with real ChromaDB."""
        # Add multiple contexts
        texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Python is a high-level programming language.",
            "FastAPI is a modern web framework.",
        ]
        
        for i, text in enumerate(texts):
            embedding = await real_sentence_transformers_encoder.encode_context(text)
            context = ContextBlock(
                id=f"test-{i}",
                content=text,
                embedding=ContextEmbedding.from_numpy(embedding)
            )
            await real_chromadb_persistence.save_context(context)
        
        # Search for similar
        query_text = "What is machine learning?"
        query_embedding = await real_sentence_transformers_encoder.encode_query(query_text)
        
        results = await real_chromadb_persistence.search_similar(query_embedding, top_k=2)
        
        assert len(results) > 0
        assert results[0].content == texts[0]  # Should match first text


@pytest.mark.integration
@pytest.mark.requires_db
class TestRealFilePersistence:
    """Test real file-based persistence."""
    
    @pytest.mark.asyncio
    async def test_save_and_load(self, real_file_persistence, real_sentence_transformers_encoder):
        """Test saving and loading with file persistence."""
        text = "Machine learning is a subset of artificial intelligence."
        embedding = await real_sentence_transformers_encoder.encode_context(text)
        
        context = ContextBlock(
            id="file-test-1",
            content=text,
            embedding=ContextEmbedding.from_numpy(embedding)
        )
        
        # Save
        await real_file_persistence.save_context(context)
        
        # Load
        loaded = await real_file_persistence.load_context("file-test-1")
        
        assert loaded is not None
        assert loaded.id == "file-test-1"
        assert loaded.content == text


@pytest.mark.integration
@pytest.mark.slow
class TestRealQueryFlow:
    """Test complete query flow with real services."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_query(
        self,
        query_handler,
        context_handler,
        sample_context_texts,
        sample_queries
    ):
        """Test complete query flow from context addition to query result."""
        # Add contexts
        context_ids = []
        for text in sample_context_texts[:3]:  # Use first 3
            context = await context_handler.add_context(text)
            context_ids.append(context.id)
        
        assert len(context_ids) == 3
        
        # Submit query
        query_id = await query_handler.submit_query(
            text=sample_queries[0],
            constraints=[]
        )
        
        assert query_id is not None
        
        # Get results
        result = await query_handler.get_result(query_id)
        
        assert result is not None
        assert result.query_id == query_id
        assert len(result.contexts) > 0
        assert result.processing_time_ms > 0
        
        # Verify contexts have scores
        for ctx in result.contexts:
            assert ctx.relevance_score is not None
            assert ctx.superfluous_score is not None
            assert ctx.noise_score is not None


