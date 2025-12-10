# Real Tests Quick Start

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -e ".[dev,embeddings,vectordb]"
```

This installs:
- ✅ pytest & pytest-asyncio (testing)
- ✅ sentence-transformers (local embeddings - **no API key needed**)
- ✅ chromadb (local vector database - **no setup needed**)

### 2. Run Real Tests
```bash
# Run integration tests (uses real Sentence Transformers + ChromaDB)
pytest -m integration

# Run all tests
pytest tests/
```

**That's it!** These tests use:
- ✅ **Real Sentence Transformers** (downloads model automatically, ~80MB)
- ✅ **Real ChromaDB** (runs locally, no server needed)
- ✅ **No API keys required** (uses local services)

---

## 📋 What You Get

### Tests Created
- ✅ `tests/conftest.py` - Test fixtures with real services
- ✅ `tests/integration/test_real_services.py` - Real integration tests

### Real Services Used
1. **Sentence Transformers** - Local embedding model (free, no API key)
2. **ChromaDB** - Local vector database (runs in-process)
3. **File Persistence** - Real file-based storage

### What's NOT Needed (for basic tests)
- ❌ OpenAI API key (only needed for OpenAI-specific tests)
- ❌ Redis server (only needed for Redis event bus tests)
- ❌ External services

---

## 🎯 Test Examples

### Test Real Encoder
```python
# Uses real Sentence Transformers
pytest tests/integration/test_real_services.py::TestRealSentenceTransformers
```

### Test Real Database
```python
# Uses real ChromaDB
pytest tests/integration/test_real_services.py::TestRealChromaDB
```

### Test Complete Flow
```python
# Uses real Sentence Transformers + ChromaDB + handlers
pytest tests/integration/test_real_services.py::TestRealQueryFlow
```

---

## 💰 Cost Breakdown

| Service | Cost | Setup Required |
|---------|------|----------------|
| Sentence Transformers | **FREE** | None (downloads model) |
| ChromaDB (local) | **FREE** | None (runs in-process) |
| File Persistence | **FREE** | None |
| OpenAI API | **~$0.0001/request** | API key |
| Redis | **FREE** (local) | Install Redis |

**For basic real tests: $0.00** ✅

---

## ⚡ Speed Comparison

| Test Type | Speed | Example |
|-----------|-------|---------|
| Mock tests | **~0.01s** | Unit tests with mocks |
| Real (local) | **~1-5s** | Sentence Transformers + ChromaDB |
| Real (API) | **~2-10s** | OpenAI API calls |

---

## 🔧 Optional: Add OpenAI Tests

If you want to test with OpenAI (costs money):

```bash
# 1. Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-key-here"

# 2. Run OpenAI tests
pytest -m requires_api
```

---

## 📊 Test Markers

```bash
# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run tests requiring API
pytest -m requires_api

# Run tests requiring database
pytest -m requires_db
```

---

## ✅ What Works Out of the Box

After `pip install -e ".[dev,embeddings,vectordb]"`:

- ✅ Real Sentence Transformers encoder
- ✅ Real ChromaDB persistence
- ✅ Real file persistence
- ✅ Real in-memory persistence
- ✅ Complete query flow tests
- ✅ Context management tests

**No additional setup needed!**

---

## 🎉 Summary

**Minimum Setup:**
1. `pip install -e ".[dev,embeddings,vectordb]"`
2. `pytest -m integration`

**That's it!** You're running real tests with:
- Real embeddings (Sentence Transformers)
- Real database (ChromaDB)
- Real handlers
- **Zero cost, zero API keys needed**

---

*Quick Start Guide - December 2025*


