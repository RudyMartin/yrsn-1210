# Real (Integration) Tests Setup Guide

This document explains what you need to run **real tests** - tests that use actual services instead of mocks.

---

## 🔴 Real Tests vs Mock Tests

### Mock Tests (Unit Tests)
- **Fast** ⚡ - No network calls
- **Free** 💰 - No API costs
- **Reliable** ✅ - No external dependencies
- **Isolated** 🔒 - Test one component at a time

### Real Tests (Integration Tests)
- **Slow** 🐌 - Network calls, database I/O
- **Costs Money** 💸 - Real API calls
- **Can Fail** ⚠️ - Depends on external services
- **Realistic** 🎯 - Tests actual integration

---

## 📋 What You Need for Real Tests

### 1. Python Dependencies

Install all optional dependencies:

```bash
# Install all dependencies
pip install -e ".[dev,api,embeddings,vectordb,observability]"

# Or install individually:
pip install pytest pytest-asyncio
pip install fastapi uvicorn
pip install openai sentence-transformers
pip install chromadb
pip install prometheus-client opentelemetry-api opentelemetry-sdk
```

### 2. External Services & APIs

#### A. OpenAI API (for OpenAI Encoder)
**Required:** API Key

```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-api-key-here"

# Or in .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

**Cost:** ~$0.0001 per 1K tokens (text-embedding-3-small)
**Setup:** Get key from https://platform.openai.com/api-keys

#### B. ChromaDB (for Vector Database)
**Options:**

1. **Local ChromaDB** (No setup needed - runs in-process)
   ```python
   # Works out of the box
   adapter = ChromaDBPersistenceAdapter(persist_directory="./test_chroma")
   ```

2. **ChromaDB Server** (Optional - for distributed testing)
   ```bash
   # Install ChromaDB server
   pip install chromadb[server]
   
   # Run server
   chroma run --path ./chroma_data --port 8000
   ```
   Then use:
   ```python
   adapter = ChromaDBPersistenceAdapter(host="localhost", port=8000)
   ```

#### C. Redis (for Event Bus - if implemented)
```bash
# Install Redis
# macOS
brew install redis
redis-server

# Linux
sudo apt-get install redis-server
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

#### D. Sentence Transformers (Local Models)
**No API key needed** - Downloads models automatically

```python
# First run downloads model (~80MB)
encoder = SentenceTransformersEncoderAdapter(model_name="all-MiniLM-L6-v2")
```

**Storage:** Models stored in `~/.cache/huggingface/`

---

## 🧪 Test Configuration

### Environment Variables

Create `.env.test` file:

```bash
# .env.test
YSRN_ENV=testing
YSRN_ENCODER_TYPE=sentence_transformers  # Use local, not OpenAI
YSRN_DB_TYPE=chromadb
YSRN_DB_PATH=./test_data/chroma
YSRN_EVENT_BUS_TYPE=in_memory
YSRN_LOG_LEVEL=DEBUG

# Optional - only if testing OpenAI
# OPENAI_API_KEY=sk-test-key

# Optional - only if testing with Redis
# YSRN_EVENT_BUS_TYPE=redis
# YSRN_EVENT_BUS_HOST=localhost
# YSRN_EVENT_BUS_PORT=6379
```

### Pytest Configuration

Create `pytest.ini` or `pyproject.toml` section:

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests (use mocks)
    integration: Integration tests (use real services)
    e2e: End-to-end tests (full system)
    slow: Slow tests (skip in CI)
    requires_api: Requires external API (OpenAI, etc.)
    requires_db: Requires database
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
    "requires_api: Requires external API",
    "requires_db: Requires database",
]
```

---

## 📝 Example Real Test Setup

### Test Fixtures for Real Services

```python
# tests/conftest.py
import pytest
import os
import shutil
from pathlib import Path

# Real adapters
from ysrn.adapters.secondary.encoder.sentence_transformers_adapter import SentenceTransformersEncoderAdapter
from ysrn.adapters.secondary.persistence.chromadb_adapter import ChromaDBPersistenceAdapter
from ysrn.adapters.secondary.persistence.file_adapter import FilePersistenceAdapter
from ysrn.adapters.secondary.event_bus.in_memory_event_bus import InMemoryEventBusAdapter

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory."""
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)

@pytest.fixture
def real_encoder():
    """Real Sentence Transformers encoder."""
    return SentenceTransformersEncoderAdapter(
        model_name="all-MiniLM-L6-v2",  # Small, fast model
        device="cpu"
    )

@pytest.fixture
def real_chromadb(test_data_dir):
    """Real ChromaDB adapter."""
    chroma_path = test_data_dir / "chroma"
    adapter = ChromaDBPersistenceAdapter(
        collection_name="test_contexts",
        persist_directory=str(chroma_path)
    )
    yield adapter
    # Cleanup
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

@pytest.fixture
def real_file_persistence(test_data_dir):
    """Real file-based persistence."""
    file_path = test_data_dir / "file_db"
    adapter = FilePersistenceAdapter(data_dir=str(file_path))
    yield adapter
    # Cleanup
    if file_path.exists():
        shutil.rmtree(file_path)

@pytest.fixture
def real_event_bus():
    """Real in-memory event bus."""
    return InMemoryEventBusAdapter()

# Mark tests that require real services
pytestmark = pytest.mark.integration
```

### Example Real Integration Test

```python
# tests/integration/test_real_query_flow.py
import pytest
import numpy as np
from ysrn.application.query_handler import QueryHandler
from ysrn.domain.service.ysrn_engine import YSRNEngine
from ysrn.domain.service.gated_retrieval import GatedContextRetriever
from ysrn.application.context_handler import ContextHandler

@pytest.mark.integration
@pytest.mark.slow
class TestRealQueryFlow:
    """Real integration tests using actual services."""
    
    @pytest.mark.asyncio
    async def test_real_query_with_sentence_transformers(
        self,
        real_encoder,
        real_chromadb,
        real_event_bus
    ):
        """Test query flow with real Sentence Transformers encoder."""
        # Setup real services
        ysrn_engine = YSRNEngine()
        retriever = GatedContextRetriever()
        
        # Create handlers with real adapters
        context_handler = ContextHandler(
            encoder=real_encoder,  # Real encoder
            persistence=real_chromadb  # Real database
        )
        
        query_handler = QueryHandler(
            ysrn_engine=ysrn_engine,
            retriever=retriever,
            encoder=real_encoder,  # Real encoder
            persistence=real_chromadb,  # Real database
            event_bus=real_event_bus
        )
        
        # Add real context
        context = await context_handler.add_context(
            content="Machine learning is a subset of artificial intelligence.",
            metadata={"source": "test"}
        )
        assert context.id is not None
        assert context.embedding is not None
        
        # Submit real query
        query_id = await query_handler.submit_query(
            text="What is machine learning?",
            constraints=[]
        )
        assert query_id is not None
        
        # Get real results
        result = await query_handler.get_result(query_id)
        assert result is not None
        assert len(result.contexts) > 0
        assert result.contexts[0].relevance_score is not None
    
    @pytest.mark.integration
    @pytest.mark.requires_api
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    async def test_real_query_with_openai(
        self,
        real_chromadb,
        real_event_bus
    ):
        """Test query flow with real OpenAI encoder."""
        from ysrn.adapters.secondary.encoder.openai_adapter import OpenAIEncoderAdapter
        
        # Real OpenAI encoder (requires API key)
        real_encoder = OpenAIEncoderAdapter(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"
        )
        
        # ... rest of test similar to above
```

---

## 🚀 Running Real Tests

### Run All Tests
```bash
pytest tests/
```

### Run Only Integration Tests
```bash
pytest -m integration
```

### Run Only Fast Tests (Skip Slow)
```bash
pytest -m "not slow"
```

### Run Tests Requiring API
```bash
# Set API key first
export OPENAI_API_KEY="sk-..."
pytest -m requires_api
```

### Run with Coverage
```bash
pytest --cov=src/ysrn --cov-report=html
```

---

## ⚠️ Important Considerations

### 1. Costs
- **OpenAI API:** Costs money per request
- **Solution:** Use Sentence Transformers for most tests, OpenAI only for specific tests

### 2. Speed
- **Real tests are slow:** 10-100x slower than mocks
- **Solution:** Mark slow tests, skip in CI for quick feedback

### 3. Reliability
- **External services can fail:** Network issues, API downtime
- **Solution:** Use retries, mark tests as flaky, have fallbacks

### 4. Test Data
- **Clean up after tests:** Don't pollute databases
- **Solution:** Use test-specific databases, cleanup fixtures

### 5. CI/CD
- **Don't run expensive tests in CI:** Costs add up
- **Solution:** Run real tests only on main branch, use mocks in PRs

---

## 📊 Recommended Test Strategy

### Unit Tests (Mocks) - 80% of tests
- Fast, free, reliable
- Test business logic
- Run in CI on every PR

### Integration Tests (Real Services) - 15% of tests
- Test adapter integrations
- Use local services (Sentence Transformers, local ChromaDB)
- Run in CI on main branch

### E2E Tests (Full System) - 5% of tests
- Test complete workflows
- Use real APIs (OpenAI) - marked with `@pytest.mark.requires_api`
- Run manually or on release

---

## 🔧 Quick Start Checklist

- [ ] Install dependencies: `pip install -e ".[dev,api,embeddings,vectordb]"`
- [ ] (Optional) Get OpenAI API key
- [ ] Create `.env.test` file
- [ ] Create `pytest.ini` or add to `pyproject.toml`
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Write integration tests
- [ ] Run tests: `pytest -m integration`

---

## 💡 Pro Tips

1. **Use local services by default** - Sentence Transformers, local ChromaDB
2. **Mark expensive tests** - Use `@pytest.mark.requires_api` for OpenAI
3. **Skip in CI** - Use `@pytest.mark.skipif` for optional services
4. **Clean up** - Always cleanup test data in fixtures
5. **Separate test databases** - Use different collection names for tests
6. **Monitor costs** - Track API usage if using paid services

---

*Real Tests Setup Guide - December 2025*


