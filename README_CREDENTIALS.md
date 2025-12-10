# 🔐 Credentials Setup - Quick Start

## ⚠️ IMPORTANT: Never Commit Real Credentials

This repository uses a **template-based approach** for credentials management.

---

## 🚀 Quick Setup (3 Steps)

### 1. Copy the Template
```bash
cp .env.template .env
```

### 2. Edit .env and Enter Your Credentials
Open `.env` in your editor and replace placeholders with your actual values:

```bash
# Example: Replace this
OPENAI_API_KEY=sk-ENTER-YOUR-OPENAI-API-KEY-HERE

# With your actual key
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Verify It's Ignored
```bash
git status
# .env should NOT appear in the list
```

---

## 📁 File Structure

| File | Status | Purpose |
|------|--------|---------|
| `.env.template` | ✅ **Committed** | Template with placeholders (safe) |
| `.env` | ❌ **NOT Committed** | Your actual credentials (ignored) |
| `.gitignore` | ✅ **Committed** | Prevents committing `.env` |

---

## 🔑 What Credentials Do I Need?

### Option 1: Local Development (No API Key Needed) ✅ Recommended

Use Sentence Transformers - it's free and works locally:

```bash
# In .env file
YSRN_ENCODER_TYPE=sentence_transformers
# No API key needed!
```

### Option 2: OpenAI Encoder (Requires API Key)

If you want to use OpenAI embeddings:

1. Get API key from: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   YSRN_ENCODER_TYPE=openai
   ```

---

## ✅ Verification

### Check .env is Ignored
```bash
git check-ignore .env
# Should output: .env
```

### Check .env.template is NOT Ignored
```bash
git check-ignore .env.template
# Should output nothing (file is tracked)
```

### Test Configuration
```python
from dotenv import load_dotenv
load_dotenv()

from ysrn.infrastructure.config import get_config
config = get_config()
print(f"Encoder: {config.encoder.type}")
```

---

## 🛡️ Security Features

The `.gitignore` includes a **"Credentials Exclude"** section that prevents committing:

- ✅ `.env` and all `.env.*` files (except `.env.template`)
- ✅ `*.key`, `*.pem`, `*.secret` files
- ✅ `secrets.json`, `credentials.json`
- ✅ Database files with credentials
- ✅ SSH keys and certificates

**Always review `.gitignore` before committing!**

---

## 📚 More Information

- **Full Guide:** See `CREDENTIALS_SETUP.md`
- **Configuration:** See `CONFIG_GUIDE.md`
- **Template File:** See `.env.template` (includes all options)

---

## 🆘 Troubleshooting

**".env is being tracked by git"**
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

**"Configuration not loading"**
```bash
# Make sure python-dotenv is installed
pip install python-dotenv

# Load in your code
from dotenv import load_dotenv
load_dotenv()
```

---

*Quick Credentials Guide - December 2025*

