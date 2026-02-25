#!/usr/bin/env python3
"""
Quick test to verify CLIP embeddings work
Tests: ImageEmbedder, EmbeddingGenerator, and basic functionality
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.embeddings import ImageEmbedder, EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("🧪 TESTING CLIP & EMBEDDING SYSTEM")
    logger.info("=" * 70 + "\n")
    
    # Test 1: ImageEmbedder initialization
    logger.info("1️⃣  Testing ImageEmbedder initialization...")
    try:
        embedder = ImageEmbedder()
        logger.info(f"   ✓ ImageEmbedder loaded")
        logger.info(f"   Model: {embedder.model_name}")
        logger.info(f"   Device: {embedder.device}")
        logger.info(f"   Dimension: {embedder.dimension}\n")
    except Exception as e:
        logger.error(f"   ✗ Failed to load ImageEmbedder: {e}\n")
        return False
    
    # Test 2: EmbeddingGenerator initialization
    logger.info("2️⃣  Testing EmbeddingGenerator initialization...")
    try:
        gen = EmbeddingGenerator()
        logger.info(f"   ✓ EmbeddingGenerator loaded\n")
    except Exception as e:
        logger.error(f"   ✗ Failed to load EmbeddingGenerator: {e}\n")
        return False
    
    # Test 3: Text embedding
    logger.info("3️⃣  Testing text embedding...")
    try:
        text = "Beautiful mountain landscape at sunset with golden light"
        emb = gen.embed_text(text)
        logger.info(f"   ✓ Text embedded successfully")
        logger.info(f"   Input: '{text[:40]}...'")
        logger.info(f"   Output: {len(emb)}-dimensional vector")
        logger.info(f"   First 5 values: {emb[:5]}\n")
    except Exception as e:
        logger.error(f"   ✗ Text embedding failed: {e}\n")
        return False
    
    # Test 4: Find sample image
    logger.info("4️⃣  Looking for sample image...")
    backend_dir = Path(__file__).parent.parent
    image_dir = backend_dir / "data" / "images"
    
    sample_image = None
    for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']:
        images = list(image_dir.glob(f"*{ext}"))
        if images:
            sample_image = images[0]
            break
    
    if not sample_image:
        logger.warning(f"   ⚠ No sample images found in {image_dir}")
        logger.info(f"   ℹ Run 'python scripts/load_images.py' to populate images\n")
        return True  # Still pass test, just skip image embedding
    
    logger.info(f"   ✓ Found sample image: {sample_image.name}\n")
    
    # Test 5: Image embedding
    logger.info("5️⃣  Testing image embedding...")
    try:
        image_emb = embedder.embed_image(str(sample_image))
        logger.info(f"   ✓ Image embedded successfully")
        logger.info(f"   Input: {sample_image.name}")
        logger.info(f"   Output: {len(image_emb)}-dimensional vector")
        logger.info(f"   First 5 values: {image_emb[:5]}\n")
    except Exception as e:
        logger.error(f"   ✗ Image embedding failed: {e}\n")
        return False
    
    # Success summary
    logger.info("=" * 70)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 70)
    logger.info("\n📋 Next Steps:")
    logger.info("   1. Load images: python scripts/load_images.py")
    logger.info("   2. Start backend: python app/main.py")
    logger.info("   3. Test API: curl http://localhost:8000/docs")
    logger.info("\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
