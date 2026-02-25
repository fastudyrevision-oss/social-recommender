"""
Embedding module for generating text and image embeddings
"""
import numpy as np
from sentence_transformers import SentenceTransformer
import open_clip
import torch
from PIL import Image
import io
import requests
from pathlib import Path
from core.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION, CLIP_MODEL, CLIP_DIMENSION, ENABLE_IMAGE_EMBEDDINGS
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize Sentence Transformer model"""
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = EMBEDDING_DIMENSION  # add dimension for test script
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def encode(self, texts: list, normalize: bool = True) -> np.ndarray:
        """Convert texts to embeddings"""
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text"""
        return self.encode([text])[0]

    # ✅ Add embed_text alias for test script
    def embed_text(self, text: str) -> np.ndarray:
        return self.encode_single(text)


# Global embedder instances
_embedder = None
_image_embedder = None

def get_embedder() -> EmbeddingGenerator:
    """Get or create global embedder instance"""
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingGenerator()
    return _embedder


class ImageEmbedder:
    """Generate image embeddings using CLIP model"""
    
    def __init__(self, model_name: str = CLIP_MODEL):
        """Initialize CLIP model (CPU-optimized for ViT-B/32)"""
        try:
            self.device = "cpu"
            self.model_name = model_name
            self.dimension = CLIP_DIMENSION  # add dimension for test script
            
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                self.model_name,
                pretrained="openai",
                device=self.device
            )
            self.model.eval()
            
            logger.info(f"Loaded CLIP model: {model_name} on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise
    
    def encode_image_from_file(self, image_path: str) -> np.ndarray:
        try:
            image = Image.open(image_path).convert("RGB")
            return self._encode_pil_image(image)
        except Exception as e:
            logger.error(f"Failed to encode image from file: {e}")
            raise

    # ✅ Alias for test script
    def embed_image(self, image_path: str) -> np.ndarray:
        return self.encode_image_from_file(image_path)
    
    def encode_image_from_url(self, image_url: str) -> np.ndarray:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            return self._encode_pil_image(image)
        except Exception as e:
            logger.error(f"Failed to encode image from URL: {e}")
            raise
    
    def encode_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return self._encode_pil_image(image)
        except Exception as e:
            logger.error(f"Failed to encode image from bytes: {e}")
            raise
    
    def _encode_pil_image(self, image: Image.Image) -> np.ndarray:
        try:
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_embedding = self.model.encode_image(image_tensor)
                image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)
            return image_embedding.cpu().numpy()[0].astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to encode PIL image: {e}")
            raise
    
    def encode_text(self, text: str) -> np.ndarray:
        try:
            text_tokens = open_clip.tokenize(text).to(self.device)
            with torch.no_grad():
                text_embedding = self.model.encode_text(text_tokens)
                text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)
            return text_embedding.cpu().numpy()[0].astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to encode text with CLIP: {e}")
            raise
    
    


def get_image_embedder() -> ImageEmbedder:
    """Get or create global image embedder instance"""
    global _image_embedder
    if _image_embedder is None and ENABLE_IMAGE_EMBEDDINGS:
        _image_embedder = ImageEmbedder()
    return _image_embedder
