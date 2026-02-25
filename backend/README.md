# Social Media Recommender System

A powerful recommendation engine using FAISS (Facebook AI Similarity Search) and Sentence Transformers for semantic similarity-based recommendations.

## Features

- **FAISS-based Similarity Search**: Fast, scalable vector similarity search
- **Sentence Transformers**: State-of-the-art text embeddings
- **Redis Caching**: Cache recommendations for repeated queries
- **PostgreSQL Database**: Store posts and user interactions
- **FastAPI**: Modern, fast API framework
- **Batch Processing**: Add multiple posts at once

## Architecture

```
┌─────────────────────┐
│   FastAPI Server    │
│    (Port 8000)      │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │          │
  ┌───▼──┐  ┌───▼──────┐
  │FAISS │  │ Sentence │
  │Index │  │Transform │
  └──────┘  └──────────┘
      │
  ┌───▼──────────┐
  │Redis Cache   │
  │(Port 6379)   │
  └──────────────┘
      │
  ┌───▼───────────┐
  │PostgreSQL DB  │
  │(Port 5432)    │
  └────────────────┘
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize database**:
```bash
python -c "from app.db import init_db; init_db()"
```

## Running the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
GET /health
```

### Add a Single Post
```bash
POST /posts/add
Content-Type: application/json

{
  "id": "post_1",
  "content": "Amazing sunset at the beach today!",
  "author": "john_doe",
  "likes": 42,
  "comments": 5,
  "shares": 2,
  "metadata": {
    "tags": ["nature", "sunset"],
    "location": "Beach"
  }
}
```

### Add Multiple Posts (Batch)
```bash
POST /posts/batch
Content-Type: application/json

[
  {
    "id": "post_1",
    "content": "First post content",
    "author": "user1"
  },
  {
    "id": "post_2",
    "content": "Second post content",
    "author": "user2"
  }
]
```

### Get Recommendations
```bash
POST /recommend
Content-Type: application/json

{
  "query": "beautiful sunset and nature photography",
  "top_k": 10
}
```

Response:
```json
{
  "query": "beautiful sunset and nature photography",
  "recommendations": [
    {
      "id": "post_1",
      "content": "Amazing sunset at the beach today!",
      "author": "john_doe",
      "likes": 42,
      "similarity": 0.89,
      "distance": 0.12
    }
  ],
  "cached": false
}
```

### Find Similar Posts
```bash
POST /similar
Content-Type: application/json

{
  "query": "summer vacation",
  "top_k": 5
}
```

### Get Embeddings
```bash
POST /embed
Content-Type: application/json

{
  "text": "Machine learning is awesome"
}
```

Response:
```json
{
  "text": "Machine learning is awesome",
  "embedding": [0.123, -0.456, ...],
  "dimension": 384
}
```

### Get Statistics
```bash
GET /stats
```

Response:
```json
{
  "index_stats": {
    "total_items": 1000,
    "dimension": 384,
    "metadata_count": 1000
  },
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384
}
```

## Configuration

Edit `.env` file to customize:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# FAISS Settings
FAISS_INDEX_PATH=faiss_index/index.bin
FAISS_METADATA_PATH=faiss_index/metadata.pkl

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2  # or other sentence-transformers models

# Recommendations
TOP_K_RECOMMENDATIONS=10
SIMILARITY_THRESHOLD=0.5

# Cache
CACHE_TTL=3600
ENABLE_CACHE=True

# API
DEBUG=True
```

## Embedding Models

Available Sentence Transformer models (trade-off between speed and accuracy):

- `all-MiniLM-L6-v2` (recommended) - Fast, 384 dimensions
- `all-mpnet-base-v2` - Accurate, 768 dimensions
- `all-distilroberta-v1` - Fast, 768 dimensions
- `paraphrase-MiniLM-L6-v2` - Fast, 384 dimensions

## Performance Tips

1. **Use appropriate embedding model**: Smaller models are faster, larger models are more accurate
2. **Enable Redis caching**: Cache frequently searched queries
3. **Batch add posts**: Add multiple posts at once for better performance
4. **Regular index maintenance**: Rebuild index periodically for large datasets

## Example Usage

```python
import requests

# Add posts
posts = [
    {
        "id": "1",
        "content": "Python is great for machine learning",
        "author": "alice"
    },
    {
        "id": "2",
        "content": "JavaScript frameworks are powerful",
        "author": "bob"
    }
]

response = requests.post("http://localhost:8000/posts/batch", json=posts)
print(response.json())

# Get recommendations
query = {
    "query": "machine learning with Python",
    "top_k": 5
}

response = requests.post("http://localhost:8000/recommend", json=query)
recommendations = response.json()
print(f"Found {len(recommendations['recommendations'])} recommendations")
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── embeddings.py        # Sentence Transformer wrapper
│   ├── recommender.py       # FAISS recommendation engine
│   ├── redis_cache.py       # Caching layer
│   └── db.py                # Database models
├── core/
│   ├── __init__.py
│   └── config.py            # Configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Troubleshooting

### "Failed to connect to Redis"
- Ensure Redis is running: `redis-cli ping` should return PONG
- Check REDIS_URL in .env

### "FAISS index not found"
- Normal on first run. Add posts to create index
- POST to `/posts/add` or `/posts/batch` first

### "Model download takes too long"
- Sentence Transformers downloads models on first use
- Be patient or use smaller models like `all-MiniLM-L6-v2`

### "Out of memory errors"
- Use smaller embedding models
- Add posts in smaller batches
- Implement incremental index building

## License

MIT

## Contributing

Pull requests are welcome!
