"""Pytest configuration and shared fixtures."""

import pytest
import os
import shutil
from pathlib import Path
import numpy as np

# Real adapters for integration tests
from ysrn.adapters.secondary.encoder.sentence_transformers_adapter import SentenceTransformersEncoderAdapter
from ysrn.adapters.secondary.persistence.chromadb_adapter import ChromaDBPersistenceAdapter
from ysrn.adapters.secondary.persistence.file_adapter import FilePersistenceAdapter
from ysrn.adapters.secondary.persistence.in_memory_adapter import InMemoryPersistenceAdapter
from ysrn.adapters.secondary.event_bus.in_memory_event_bus import InMemoryEventBusAdapter

# Domain services
from ysrn.domain.service.ysrn_engine import YSRNEngine
from ysrn.domain.service.gated_retrieval import GatedContextRetriever

# Application handlers
from ysrn.application.query_handler import QueryHandler
from ysrn.application.context_handler import ContextHandler


# Test data directory
TEST_DATA_DIR = Path("./test_data")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before all tests."""
    # Create test data directory
    TEST_DATA_DIR.mkdir(exist_ok=True)
    yield
    # Cleanup after all tests
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


# ============================================================================
# Real Service Fixtures (for integration tests)
# ============================================================================

@pytest.fixture
def real_sentence_transformers_encoder():
    """Real Sentence Transformers encoder (local, no API key needed)."""
    return SentenceTransformersEncoderAdapter(
        model_name="all-MiniLM-L6-v2",  # Small, fast model
        device="cpu"
    )


@pytest.fixture
def real_chromadb_persistence():
    """Real ChromaDB adapter with test database."""
    chroma_path = TEST_DATA_DIR / "chroma_test"
    adapter = ChromaDBPersistenceAdapter(
        collection_name="test_contexts",
        persist_directory=str(chroma_path)
    )
    yield adapter
    # Cleanup
    if chroma_path.exists():
        shutil.rmtree(chroma_path)


@pytest.fixture
def real_file_persistence():
    """Real file-based persistence adapter."""
    file_path = TEST_DATA_DIR / "file_test"
    adapter = FilePersistenceAdapter(data_dir=str(file_path))
    yield adapter
    # Cleanup
    if file_path.exists():
        shutil.rmtree(file_path)


@pytest.fixture
def real_in_memory_persistence():
    """Real in-memory persistence (fast, no cleanup needed)."""
    return InMemoryPersistenceAdapter()


@pytest.fixture
def real_event_bus():
    """Real in-memory event bus."""
    return InMemoryEventBusAdapter()


@pytest.fixture
def real_openai_encoder():
    """Real OpenAI encoder (requires API key)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    
    from ysrn.adapters.secondary.encoder.openai_adapter import OpenAIEncoderAdapter
    return OpenAIEncoderAdapter(
        api_key=api_key,
        model="text-embedding-3-small"
    )


# ============================================================================
# Domain Service Fixtures
# ============================================================================

@pytest.fixture
def ysrn_engine():
    """YSRN Engine instance."""
    return YSRNEngine(
        relevance_threshold=0.3,
        noise_threshold=0.1,
        num_components=64
    )


@pytest.fixture
def gated_retriever():
    """Gated Context Retriever instance."""
    return GatedContextRetriever(
        num_heads=8,
        head_dim=64,
        gate_init_bias=-2.0
    )


# ============================================================================
# Application Handler Fixtures
# ============================================================================

@pytest.fixture
def query_handler(
    ysrn_engine,
    gated_retriever,
    real_sentence_transformers_encoder,
    real_in_memory_persistence,
    real_event_bus
):
    """Query handler with real adapters."""
    return QueryHandler(
        ysrn_engine=ysrn_engine,
        retriever=gated_retriever,
        encoder=real_sentence_transformers_encoder,
        persistence=real_in_memory_persistence,
        event_bus=real_event_bus
    )


@pytest.fixture
def context_handler(
    real_sentence_transformers_encoder,
    real_in_memory_persistence
):
    """Context handler with real adapters."""
    return ContextHandler(
        encoder=real_sentence_transformers_encoder,
        persistence=real_in_memory_persistence
    )


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_context_texts():
    """Sample context texts for testing."""
    return [
        "Machine learning is a subset of artificial intelligence.",
        "Python is a high-level programming language.",
        "FastAPI is a modern web framework for building APIs.",
        "Vector databases store embeddings for similarity search.",
        "Hexagonal architecture separates business logic from infrastructure.",
    ]


@pytest.fixture
def sample_queries():
    """Sample queries for testing."""
    return [
        "What is machine learning?",
        "Tell me about Python programming",
        "How does FastAPI work?",
        "What are vector databases?",
        "Explain hexagonal architecture",
    ]


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: Integration tests using real services"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that should be skipped in CI"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests requiring external API (OpenAI, etc.)"
    )
    config.addinivalue_line(
        "markers", "requires_db: Tests requiring database"
    )


