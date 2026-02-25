# Sentence Transformers - Technical Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SOCIAL RECOMMENDER SYSTEM                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
│                  User Posts, Search, Recommendations                │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
├─────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │          EmbeddingGenerator (embeddings.py)                  │   │
│ │                                                               │   │
│ │  from sentence_transformers import SentenceTransformer      │   │
│ │                                                               │   │
│ │  model = SentenceTransformer("all-MiniLM-L6-v2")           │   │
│ │         └─> Loads from cache or downloads (first time)     │   │
│ │                                                               │   │
│ │  embeddings = model.encode(texts)                           │   │
│ │         └─> Returns 384-dimensional vectors                │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                     ▲                                               │
│                     │                                               │
│   ┌─────────────────┼──────────────────────────────────────┐       │
│   │                 │                                      │       │
│   ▼                 ▼                                      ▼       │
│ ┌──────────────┐ ┌──────────┐ ┌─────────────────────────┐         │
│ │  Recommender │ │ Redis    │ │   FAISS Index           │         │
│ │   Engine     │ │  Cache   │ │ (Vector Database)       │         │
│ │ (rank posts) │ │ (vectors)│ │ • index.bin (vectors)   │         │
│ └──────────────┘ └──────────┘ │ • metadata.pkl (posts)  │         │
│                                │ (Similarity Search)     │         │
│                                └─────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                     │
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐ ┌────────────┐ ┌──────────┐
   │PostgreSQL│ │ HuggingFace│ │  Local   │
   │Database  │ │   Hub      │ │  Cache   │
   │(posts)   │ │(model repo)│ │(~150 MB) │
   └─────────┘ └────────────┘ └──────────┘
                      │
              (Internet - First Time Only)
```

---

## Data Flow: From Post to Recommendation

```
Step 1: User Creates Post
┌──────────────────────┐
│ "Great sunset today" │
└──────────┬───────────┘
           │
           ▼
Step 2: Extract Text Content
┌──────────────────────┐
│ "Great sunset today" │
└──────────┬───────────┘
           │
           ▼
Step 3: Send to EmbeddingGenerator
┌────────────────────────────────────────────┐
│ EmbeddingGenerator.encode([text])          │
│                                            │
│  1. Tokenizes text (WordPiece)            │
│  2. Passes through SentenceTransformer    │
│  3. Returns 384-dim vector                │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 4: Store in FAISS Index
┌────────────────────────────────────────────┐
│ Vector: [0.234, -0.512, 0.876, ...]      │ (384 dims)
│ Post ID: post_12345                      │
│ Metadata: {author, created_at, ...}      │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 5: Cache in Redis (Optional)
┌────────────────────────────────────────────┐
│ key: post_embeddings:12345                │
│ value: [0.234, -0.512, 0.876, ...]       │
│ ttl: 3600 seconds                        │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 6: User Searches/Gets Recommendations
┌────────────────────────────────────────────┐
│ Similar Posts Query                       │
│ User's Post Vector → FAISS Search         │
│ Return Top K Most Similar Posts           │
└────────────────────────────────────────────┘
```

---

## File Structure

```
backend/
├── app/
│   ├── embeddings.py          ← EmbeddingGenerator class
│   │   └── Uses: SentenceTransformer("all-MiniLM-L6-v2")
│   │       │
│   │       └─> First Load: Downloads from Hugging Face
│   │       └─> After: Loads from ~/.cache/huggingface/
│   │
│   ├── recommender.py         ← Calls EmbeddingGenerator
│   ├── main.py                ← FastAPI app
│   └── db.py                  ← Database operations
│
├── core/
│   └── config.py
│       ├── EMBEDDING_MODEL = "all-MiniLM-L6-v2"
│       └── EMBEDDING_DIMENSION = 384
│
├── requirements.txt
│   ├── sentence-transformers==5.1.2
│   ├── transformers==4.57.3
│   ├── torch==2.9.1
│   └── ...other dependencies...
│
├── faiss_index/
│   ├── index.bin              ← FAISS vector index
│   └── metadata.pkl           ← Post metadata mapping
│
└── venv/
    └── lib/python3.12/site-packages/
        └── sentence_transformers/  ← Installed package
```

---

## Model Loading Sequence Diagram

```
Time ──────────────────────────────────────────>

Application Startup
    │
    ├─> Import SentenceTransformer class
    │       (from installed pip package)
    │
    ├─> EmbeddingGenerator.__init__()
    │       │
    │       ├─> SentenceTransformer("all-MiniLM-L6-v2")
    │       │
    │       ├─ Check: Is model in ~/.cache/huggingface/ ?
    │       │
    │       ├─ IF YES:
    │       │   └─> Load from cache (< 1 second)
    │       │       Model ready to use
    │       │
    │       └─ IF NO (First time):
    │           └─> Download from huggingface.co (30-60 sec)
    │               Save to ~/.cache/huggingface/
    │               Load into memory
    │               Model ready to use
    │
    ├─> Embeddings ready
    │   encode() method available
    │
    └─> First request comes in
        ├─> EmbeddingGenerator.encode(texts)
        │   └─> texts → 384-dim vectors
        │
        └─> Store in FAISS/Redis
            Ready for similarity search
```

---

## Configuration & Customization

```
config.py
│
├─ EMBEDDING_MODEL (environment variable)
│  │
│  ├─ "all-MiniLM-L6-v2" (Default)
│  │  ├─ Size: 27 MB
│  │  ├─ Dims: 384
│  │  ├─ Speed: Fast
│  │  └─ Use: General similarity
│  │
│  ├─ "all-mpnet-base-v2"
│  │  ├─ Size: 438 MB
│  │  ├─ Dims: 768
│  │  ├─ Speed: Medium
│  │  └─ Use: High accuracy
│  │
│  └─ "all-roberta-large-v1"
│     ├─ Size: 1.3 GB
│     ├─ Dims: 1024
│     ├─ Speed: Slow
│     └─ Use: Very high accuracy
│
└─ EMBEDDING_DIMENSION
   └─ Auto-matches selected model
```

---

## Caching Mechanism

```
Request for embeddings:
    │
    ├─> Check Redis Cache
    │   ├─ Cache HIT:
    │   │  └─> Return cached vector (< 1ms)
    │   │
    │   └─ Cache MISS:
    │       ├─> Generate embedding
    │       │   └─> SentenceTransformer.encode()
    │       │
    │       ├─> Store in Redis
    │       │   └─> TTL: 3600 seconds
    │       │
    │       └─> Return to caller
│
└─ Reduce computation:
   └─ Skip expensive embedding generation
      for same posts
```

---

## Performance Metrics

```
Model: all-MiniLM-L6-v2

Metric                  | Value
───────────────────────────────────
Download Size           | 27 MB
Extracted Size          | ~150 MB (with deps)
Embedding Dimension     | 384
Model Parameters        | 22.7M
Memory Usage (loaded)   | ~500 MB RAM
Inference Speed         | ~1000 texts/sec
Batch Processing        | ~5000 texts/sec
GPU Support             | Yes (if available)
CPU Inference           | Optimized & Fast
```

---

## Network/Internet Requirements

```
Installation Phase
├─ pip install sentence-transformers
│  └─ Internet: YES (PyPI)
│     First-time only
│
Application Runtime
├─ First Startup
│  ├─ Model load
│  │  └─ If cached:
│  │     └─ Internet: NO
│  │  └─ If not cached:
│  │     └─ Internet: YES (Hugging Face)
│  │        30-60 seconds
│  │        Downloads ~27 MB
│  │
│  └─ Subsequent runs:
│     └─ Internet: NO (uses cache)
│
Docker/Production
├─ Build Phase
│  ├─ Pre-download model in Dockerfile
│  └─ Internet: YES
│
└─ Runtime Phase
   └─ Internet: NO
      (model already in image)
```

---

## Troubleshooting

### Issue: Model not loading
```python
# Debug: Check cache location
import sentence_transformers
print(sentence_transformers.__file__)

# Check cache
import os
cache_path = os.path.expanduser("~/.cache/huggingface")
print(os.listdir(cache_path))
```

### Issue: Slow first startup
- **Expected:** First startup takes 30-60 seconds (downloading model)
- **Solution:** Pre-download in Docker or CI/CD

### Issue: Out of memory
- **Current Model:** Uses ~500 MB RAM
- **Solution:** Smaller model like "all-MiniLM-L6-v2" (already selected)

### Issue: Need offline mode
```python
# Pre-download model offline
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
# Then use local_files_only=True on subsequent loads
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Installation** | ✅ Via pip (already installed) |
| **Model** | all-MiniLM-L6-v2 (384 dims) |
| **Download** | From Hugging Face (first time only) |
| **Cache** | ~/.cache/huggingface/ (~150 MB) |
| **Internet** | Only needed for first model load |
| **Speed** | Fast (~1000 texts/sec) |
| **Memory** | ~500 MB RAM |
| **Production** | Pre-download in Docker |
