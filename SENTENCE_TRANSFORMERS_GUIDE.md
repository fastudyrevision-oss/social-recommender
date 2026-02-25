# Sentence Transformers - System Usage & Architecture

## Overview
The Social Recommender system uses **Sentence Transformers** to convert text (posts, captions, descriptions) into numerical embeddings that capture semantic meaning. These embeddings enable similarity-based recommendations.

---

## 📦 Installation & Loading

### How It's Installed
✅ **You installed it via pip:**
```bash
pip install sentence-transformers==5.1.2
```

### Where It's Listed
**File:** `/backend/requirements.txt`
```
sentence-transformers==5.1.2
transformers==4.57.3
torch==2.9.1
```

### How It Works in the System

**No, it does NOT load from the internet after installation.** Here's how it works:

---

## 🔄 Model Loading Process

### Step 1: First Time Usage
When you first run the application and Sentence Transformers encounters a model it hasn't loaded before:

```python
# backend/app/embeddings.py
self.model = SentenceTransformer(model_name)
```

**What happens:**
1. Sentence Transformers checks if model exists locally (in `~/.cache/huggingface/`)
2. If NOT found → Downloads model from Hugging Face Hub (internet required)
3. If FOUND → Loads from local cache (no internet needed)

### Step 2: Model Configuration
**File:** `/backend/core/config.py`
```python
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2
```

**Model Details:**
- **Name:** `all-MiniLM-L6-v2`
- **Size:** ~27 MB
- **Speed:** Very fast
- **Dimensions:** 384-dimensional vectors
- **Purpose:** General-purpose semantic similarity

---

## 💾 Where Models Are Cached

### Local Cache Location
After first download, models are stored at:

**Linux/Mac:**
```
~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/
```

**Windows:**
```
C:\Users\{username}\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\
```

### File Structure
```
~/.cache/huggingface/hub/
├── models--sentence-transformers--all-MiniLM-L6-v2/
│   ├── snapshots/
│   │   └── {commit_hash}/
│   │       ├── config.json
│   │       ├── model.safetensors
│   │       ├── tokenizer_config.json
│   │       ├── tokenizer.json
│   │       ├── special_tokens_map.json
│   │       └── ...
│   └── blobs/
```

---

## 🎯 How It's Used in Your System

### 1. **Initialization** (First Time Only)
```python
# backend/app/embeddings.py
class EmbeddingGenerator:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        try:
            self.model = SentenceTransformer(model_name)  # Loads from cache or downloads
            logger.info(f"Loaded embedding model: {model_name}")
```

### 2. **Text to Embeddings Conversion**
```python
def encode(self, texts: list) -> np.ndarray:
    embeddings = self.model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True  # Normalize for similarity search
    )
    return embeddings.astype(np.float32)  # 384-dimensional vectors
```

### 3. **Usage in Recommendation Engine**
```
Post Content → Sentence Transformer → 384-dim Vector
                      ↓
              FAISS Index Storage
                      ↓
          Similarity Comparison with User Behavior
                      ↓
          Ranked Recommendations
```

---

## 📊 Flow Diagram

```
User Input (Post Caption)
         ↓
    [Sentence Transformer]
    (all-MiniLM-L6-v2)
         ↓
   384-Dimensional Vector
    (Semantic Embedding)
         ↓
    [FAISS Index]
    (Vector Database)
         ↓
Similarity Search
(Cosine Similarity)
         ↓
Ranked Recommendations
```

---

## 🚀 When Internet is Used vs. Not Used

### ✅ Internet Required (First Time Only):
1. **First application startup** with new model
2. Running in a new environment/container
3. Model cache cleared manually

### ❌ Internet NOT Required:
1. **Subsequent application runs** ← Model cached locally
2. **After first download** ← Always loads from cache
3. **Production deployment** ← Model pre-downloaded in Docker

---

## 🔧 Code Implementation Details

### EmbeddingGenerator Class
**File:** `/backend/app/embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Initialization (loads model from cache or downloads)
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: list) -> np.ndarray:
        # Convert texts to embeddings
        return self.model.encode(texts, convert_to_numpy=True)
    
    def encode_single(self, text: str) -> np.ndarray:
        # Convert single text to embedding
        return self.encode([text])[0]

# Global embedder instance (initialized once)
_embedder = None
```

### How It's Called in FastAPI
```python
# backend/app/recommender.py
def get_embeddings(texts: list) -> np.ndarray:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingGenerator()
    return _embedder.encode(texts)
```

---

## 📈 Performance Characteristics

### Model: all-MiniLM-L6-v2
| Metric | Value |
|--------|-------|
| **Model Size** | ~27 MB |
| **Embedding Dimension** | 384 |
| **Inference Speed** | Fast (~1000 texts/sec) |
| **Memory Usage** | Low (~500 MB RAM) |
| **Download Time** | ~30-60 seconds |
| **Cache Size** | ~150 MB (with dependencies) |

---

## 🔐 Environment Variables

You can customize the model via environment variables:

**File:** `.env` (if you have one)
```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Alternative Models (if you want to change):
```python
# Smaller, faster
"all-MiniLM-L6-v2"      # 384 dims, ~27 MB

# Larger, more accurate
"all-mpnet-base-v2"     # 768 dims, ~438 MB
"all-roberta-large-v1"  # 1024 dims, ~1.3 GB

# Lightweight
"sentence-t5-base"      # 768 dims, ~220 MB
```

---

## 🌐 Internet Usage Summary

### Your Setup:
```
✅ Pip Installation
   ↓
   └── sentence-transformers==5.1.2 installed locally

✅ First Model Load
   ↓
   ├── Internet: Download model from Hugging Face
   └── Cached: ~/.cache/huggingface/hub/

✅ Subsequent Runs
   ↓
   └── Internet: NOT NEEDED (loads from cache)

✅ Production Docker
   ↓
   ├── Pre-download model in Dockerfile
   └── No internet needed at runtime
```

---

## 🐳 Docker Implementation

If deployed in Docker, the Dockerfile can pre-download the model:

```dockerfile
FROM python:3.12

# Install dependencies
RUN pip install -r requirements.txt

# Pre-download the model (optional but recommended)
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('all-MiniLM-L6-v2')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📋 Dependency Chain

```
sentence-transformers==5.1.2
├── transformers==4.57.3
├── torch==2.9.1
├── huggingface-hub (downloads models)
└── numpy, scipy, scikit-learn
```

---

## ✨ Key Takeaways

1. **✅ Installed via pip** - It's in your environment
2. **📥 First time** - Downloads model from Hugging Face (internet needed)
3. **💾 After download** - Cached locally (~150 MB)
4. **🚀 Subsequent runs** - Loads from cache (no internet needed)
5. **🔄 Embedding process** - Text → 384-dimensional vectors → Similarity search
6. **⚡ Performance** - Fast & lightweight for real-time recommendations

---

## 🔗 Useful Resources

- **Sentence Transformers:** https://www.sbert.net/
- **Model Hub:** https://huggingface.co/sentence-transformers
- **Cache Location:** `~/.cache/huggingface/`
- **API Docs:** https://www.sbert.net/docs/usage/semantic_textual_similarity.html

---

## ❓ FAQ

**Q: Does it download every time the app starts?**
A: No. Only the first time, then it uses the cached version.

**Q: Can I change the model?**
A: Yes, modify `EMBEDDING_MODEL` in `/backend/core/config.py` or set the environment variable.

**Q: How much storage does the model take?**
A: About 150-200 MB total (including dependencies).

**Q: Is internet required for production?**
A: No, if you pre-download the model in the Docker image.

**Q: How fast are embeddings generated?**
A: Very fast, typically 1000+ texts per second on CPU.
