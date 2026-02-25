import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://recommender:strongpassword@localhost/recsys"
)

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# API
API_TITLE = "Social Media Recommender API"
API_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# FAISS Index
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index/index.bin")
FAISS_METADATA_PATH = os.getenv("FAISS_METADATA_PATH", "faiss_index/metadata.pkl")

# Sentence Transformer Model (Text)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2

# CLIP Model (Vision + Text)
CLIP_MODEL = os.getenv("CLIP_MODEL", "ViT-B-32")  # Lightweight for CPU
CLIP_DIMENSION = 512  # ViT-B/32 output dimension
ENABLE_IMAGE_EMBEDDINGS = os.getenv("ENABLE_IMAGE_EMBEDDINGS", "True") == "True"

# Recommendation Settings
TOP_K_RECOMMENDATIONS = int(os.getenv("TOP_K_RECOMMENDATIONS", "10"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# Cache Settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True") == "True"
