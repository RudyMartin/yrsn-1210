# Configuration Guide

## 🔐 Security Warning

**NEVER commit API keys or secrets to git!** Always use environment variables or `.env` files that are in `.gitignore`.

---

## 📋 Configuration Options

The YSRN system supports configuration via:

1. **Environment Variables** (recommended)
2. **`.env` file** (for local development)
3. **JSON config file** (for complex configurations)

---

## 🚀 Quick Start

### Option 1: Environment Variables (Recommended)

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Set encoder type
export YSRN_ENCODER_TYPE="openai"

# Run your application
python scripts/run_api.py
```

### Option 2: .env File (Local Development)

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   YSRN_ENCODER_TYPE=openai
   ```

3. **Load the .env file** (you may need python-dotenv):
   ```bash
   pip install python-dotenv
   ```

   Then in your code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Loads .env file
   ```

---

## 🔧 Configuration System

The configuration system automatically reads from environment variables:

```python
from ysrn.infrastructure.config import get_config

config = get_config()

# Access configuration
print(config.encoder.type)  # "openai", "sentence_transformers", etc.
print(config.encoder.api_key)  # From OPENAI_API_KEY env var
print(config.database.type)  # "chromadb", "file", "in_memory"
```

---

## 📝 Environment Variables Reference

### Encoder Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `YSRN_ENCODER_TYPE` | `simple` | `simple`, `sentence_transformers`, or `openai` |
| `YSRN_ENCODER_MODEL` | `all-MiniLM-L6-v2` | Model name for Sentence Transformers |
| `YSRN_ENCODER_DEVICE` | `cpu` | `cpu` or `cuda` |
| `OPENAI_API_KEY` | - | Your OpenAI API key |
| `OPENAI_ORGANIZATION` | - | OpenAI organization ID (optional) |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `YSRN_DB_TYPE` | `in_memory` | `in_memory`, `file`, or `chromadb` |
| `YSRN_DB_PATH` | - | Path for file or ChromaDB storage |
| `YSRN_DB_COLLECTION` | `ysrn_contexts` | ChromaDB collection name |
| `YSRN_DB_HOST` | - | ChromaDB server host (optional) |
| `YSRN_DB_PORT` | - | ChromaDB server port (optional) |

### Event Bus Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `YSRN_EVENT_BUS_TYPE` | `in_memory` | `in_memory`, `redis`, or `kafka` |
| `YSRN_EVENT_BUS_HOST` | - | Redis/Kafka host |
| `YSRN_EVENT_BUS_PORT` | - | Redis/Kafka port |
| `YSRN_EVENT_BUS_TOPIC` | `ysrn_events` | Kafka topic name |

### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `YSRN_METRICS_ENABLED` | `true` | Enable Prometheus metrics |
| `YSRN_TRACING_ENABLED` | `true` | Enable OpenTelemetry tracing |
| `YSRN_LOG_LEVEL` | `INFO` | Logging level |
| `YSRN_PROMETHEUS_PORT` | `9090` | Prometheus metrics port |
| `JAEGER_ENDPOINT` | - | Jaeger tracing endpoint |

---

## 💡 Usage Examples

### Example 1: Using OpenAI Encoder

```bash
export OPENAI_API_KEY="sk-your-key"
export YSRN_ENCODER_TYPE="openai"
```

### Example 2: Using Sentence Transformers (Local, Free)

```bash
export YSRN_ENCODER_TYPE="sentence_transformers"
export YSRN_ENCODER_MODEL="all-MiniLM-L6-v2"
```

### Example 3: Using ChromaDB

```bash
export YSRN_DB_TYPE="chromadb"
export YSRN_DB_PATH="./data/chroma"
```

### Example 4: Complete Configuration

```bash
# .env file
OPENAI_API_KEY=sk-your-key-here
YSRN_ENCODER_TYPE=openai
YSRN_DB_TYPE=chromadb
YSRN_DB_PATH=./data/chroma
YSRN_EVENT_BUS_TYPE=in_memory
YSRN_LOG_LEVEL=DEBUG
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**
   - Add `.env` to `.gitignore`
   - Use `.env.example` as a template

2. **Use environment variables in production**
   - Set via your deployment platform (Kubernetes, Docker, etc.)
   - Never hardcode secrets

3. **Rotate API keys regularly**
   - If a key is exposed, rotate it immediately
   - Use different keys for dev/staging/production

4. **Use secret management services**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets

---

## 🐛 Troubleshooting

### API Key Not Working

```python
# Check if key is loaded
from ysrn.infrastructure.config import get_config
config = get_config()
print(config.encoder.api_key)  # Should show your key (masked in logs)
```

### Configuration Not Loading

```python
# Force reload from environment
from ysrn.infrastructure.config import YSRNConfig, set_config
config = YSRNConfig.from_env()
set_config(config)
```

---

*Configuration Guide - December 2025*

