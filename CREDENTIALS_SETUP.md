# Credentials Setup Guide

## 🔐 Security First

**NEVER commit files with real credentials to git!**

This guide shows you how to safely set up credentials for local development.

> **📋 Related Files:**
> - **`.gitignore`** - Contains "Credentials Exclude" section (lines 36-85) that prevents committing credential files
> - **`.env.template`** - Template file with placeholders (safe to commit)
> - **`README_CREDENTIALS.md`** - Quick start guide
> - **`CONFIG_GUIDE.md`** - Full configuration documentation

---

## 📋 Quick Setup (3 Steps)

### Step 1: Copy the Template
```bash
cp .env.template .env
```

### Step 2: Edit .env and Enter Your Credentials
```bash
# Open .env in your editor
nano .env
# or
code .env
```

Fill in your actual credentials (see instructions below).

### Step 3: Verify It's Ignored
```bash
# Check that .env is in .gitignore
git status
# .env should NOT appear in the list
```

---

## 🔑 Required Credentials

### For OpenAI Encoder (Optional)

If you want to use OpenAI embeddings:

1. **Get API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Add to .env:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   YSRN_ENCODER_TYPE=openai
   ```

### For Local Development (No API Key Needed)

You can use Sentence Transformers (free, local):

```bash
YSRN_ENCODER_TYPE=sentence_transformers
# No API key needed!
```

---

## 📁 File Structure

```
yrsn-1210/
├── .env.template          ✅ Committed to repo (template only)
│                          📍 Referenced in .gitignore line 113 (!.env.template)
├── .env                   ❌ NOT committed (your actual credentials)
│                          📍 Excluded by .gitignore line 43 (.env)
├── .gitignore             ✅ Committed (includes "Credentials Exclude" section)
│                          📍 Lines 36-85: Credentials Exclude section
│                          📍 Line 113: Explicit allow for .env.template
│                          📍 References: CREDENTIALS_SETUP.md (line 45)
└── CREDENTIALS_SETUP.md   ✅ Committed (this file)
                          📍 Referenced in .gitignore line 45
```

### File Relationships

- **`.gitignore` → `CREDENTIALS_SETUP.md`**: `.gitignore` references this guide (line 45)
- **`CREDENTIALS_SETUP.md` → `.gitignore`**: This guide references `.gitignore` section (lines 36-85)
- **`.env.template`**: Safe to commit, referenced in `.gitignore` line 113
- **`.env`**: Never committed, excluded by `.gitignore` line 43

---

## ✅ Verification

### Check .env is Ignored
```bash
git status
# .env should NOT appear
```

### Test Configuration Loading
```python
from dotenv import load_dotenv
load_dotenv()

from ysrn.infrastructure.config import get_config
config = get_config()

# Check if credentials loaded
if config.encoder.type == "openai":
    if config.encoder.api_key:
        print("✓ OpenAI API key loaded")
    else:
        print("✗ OpenAI API key missing")
else:
    print(f"✓ Using {config.encoder.type} encoder (no API key needed)")
```

---

## 🚨 Security Checklist

Before committing code:

- [ ] `.env` file exists locally but is NOT in git
- [ ] `.env.template` is in git (template only, no real credentials)
- [ ] `.gitignore` includes `.env` and other credential patterns
- [ ] No API keys in code files
- [ ] No hardcoded credentials anywhere
- [ ] Different keys for dev/staging/production

---

## 🔄 For Team Members

When cloning the repo:

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Get your own credentials:**
   - Ask team lead for API keys (if needed)
   - Or use local services (Sentence Transformers, no key needed)

3. **Fill in .env:**
   - Edit `.env` with your credentials
   - Never commit `.env` to git

---

## 📝 Template File Details

### `.env.template` (Committed to Repo)
- ✅ Safe to commit
- ✅ Contains placeholders only
- ✅ Includes setup instructions
- ✅ Documents all configuration options

### `.env` (Local Only)
- ❌ Never commit
- ✅ Contains your actual credentials
- ✅ Loaded automatically by application
- ✅ Already in `.gitignore`

---

## 🛠️ Troubleshooting

### "API key not found"
```bash
# Check if .env exists
ls -la .env

# Check if key is set
grep OPENAI_API_KEY .env

# Reload environment
source .env  # or restart your terminal
```

### ".env is being tracked by git"
```bash
# Remove from git (but keep local file)
git rm --cached .env

# Verify it's ignored
git status
```

### "Configuration not loading"
```python
# Force reload
from dotenv import load_dotenv
load_dotenv(override=True)  # Override existing env vars
```

---

## 🔒 Credential Patterns in .gitignore

The `.gitignore` file includes a **"Credentials Exclude"** section (starting at line 36) that prevents committing credential files to git.

### Location in .gitignore
- **Section:** Lines 36-85 (marked with `# Credentials Exclude`)
- **Purpose:** Prevent accidental commit of sensitive files
- **Reference:** See `.gitignore` for complete list of excluded patterns

### Files Excluded by .gitignore

The following patterns are automatically excluded:

- **Environment files:** `.env`, `.env.local`, `.env.*.local`, `.env.production`, etc.
- **API Keys:** `*.key`, `*.pem`, `*.secret` files
- **Secret files:** `secrets.json`, `credentials.json`, `api_keys.txt`
- **Config files:** `config.local.json`, `config.production.json`, `settings.local.py`
- **Database files:** `*.db`, `*.sqlite`, `database.ini`
- **SSH keys:** `id_rsa`, `id_ed25519`, `*.ppk`
- **Certificates:** `*.crt`, `*.cer`, `*.p12`, `*.pfx`
- **Tokens:** `*.token`, `tokens.txt`

### Files Explicitly Allowed

- **`.env.template`** - Template file (safe to commit, contains placeholders only)
  - Located in `.gitignore` line 113: `!.env.template`
  - This allows the template to be committed for team use

### How .gitignore Works

1. **Default exclusion:** All `.env*` files are ignored
2. **Explicit allow:** `.env.template` is explicitly allowed with `!.env.template`
3. **Pattern matching:** All credential patterns match before the allow rule

### Verification

To verify your `.env` is properly ignored:

```bash
# Check if .env is ignored
git check-ignore .env
# Should output: .env

# Check if .env.template is NOT ignored
git check-ignore .env.template
# Should output nothing (file can be committed)
```

**⚠️ Always review `.gitignore` before committing to ensure no credentials leak!**

> **📝 Note:** The `.gitignore` file references this document. See `.gitignore` lines 36-45 for the cross-reference.

---

## 📚 Related Files

- `.env.template` - Template file (safe to commit)
- `.gitignore` - Git ignore rules (includes credential patterns)
- `CONFIG_GUIDE.md` - Full configuration documentation
- `QUICK_CONFIG.md` - Quick reference

---

*Credentials Setup Guide - December 2025*

