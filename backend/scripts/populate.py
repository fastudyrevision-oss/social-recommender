#!/usr/bin/env python3
"""
Load 100 images from CSV and populate database with CLIP embeddings
Images are already in backend/data/images folder
Uses photo_id to match images with CSV data
"""

import os
import sys
import csv
import time
import pickle
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal, Base, engine, Post
from app.embeddings import EmbeddingGenerator, ImageEmbedder
from sqlalchemy.exc import IntegrityError

class ImageLoader:
    def __init__(self, csv_path: str, image_dir: str):
        self.csv_path = csv_path
        self.image_dir = image_dir
        self.embedding_gen = EmbeddingGenerator()
        self.image_embedder = ImageEmbedder()
        self.db = SessionLocal()
        
        self.stats = {
            'total': 0,
            'loaded': 0,
            'skipped': 0,
            'failed': 0,
            'no_image': 0
        }
    
    def read_csv(self) -> list:
        """Read CSV with tab separation"""
        logger.info(f"📖 Reading CSV: {self.csv_path}")
        data = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    data.append(row)
            logger.info(f"✓ Read {len(data)} rows\n")
            return data
        except Exception as e:
            logger.error(f"✗ Failed to read CSV: {e}")
            return []
    
    def find_image(self, photo_id: str) -> str:
        """Find image file by photo_id"""
        # Try common extensions
        for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']:
            image_path = os.path.join(self.image_dir, f"{photo_id}{ext}")
            if os.path.exists(image_path):
                return image_path
        return None
    
    def create_content(self, row: dict) -> str:
        """Create post content from CSV row"""
        parts = []
        
        # Description
        desc = row.get('photo_description', '').strip()
        if desc:
            parts.append(desc)
        
        # AI description (more detailed)
        ai_desc = row.get('ai_description', '').strip()
        if ai_desc:
            parts.append(ai_desc)
        
        # Location
        location = row.get('photo_location_name', '').strip()
        if location:
            parts.append(f"Location: {location}")
        
        # Camera info
        camera = row.get('exif_camera_model', '').strip()
        if camera:
            parts.append(f"Camera: {camera}")
        
        content = " | ".join(parts) if parts else "Beautiful photograph"
        return content[:500]  # Limit to 500 chars
    
    def load_image(self, row: dict) -> bool:
        """Load single image into database"""
        photo_id = row.get('photo_id', '').strip()
        
        if not photo_id:
            self.stats['failed'] += 1
            return False
        
        # Check if already exists
        existing = self.db.query(Post).filter(Post.id == photo_id).first()
        if existing:
            logger.info(f"  ℹ Already in DB: {photo_id}")
            self.stats['skipped'] += 1
            return True
        
        # Find image file
        image_path = self.find_image(photo_id)
        if not image_path:
            logger.warning(f"  ⚠ Image not found: {photo_id}")
            self.stats['no_image'] += 1
            return False
        
        try:
            # Create content
            content = self.create_content(row)
            logger.info(f"  📝 Content: {content[:40]}...")
            
            # Generate text embedding
            logger.info(f"  ⚙ Text embedding...")
            text_emb = self.embedding_gen.embed_text(content)
            logger.info(f"  ✓ Text: {len(text_emb)}-dim")
            
            # Generate image embedding
            logger.info(f"  🖼 Image embedding...")
            image_emb = self.image_embedder.embed_image(image_path)
            logger.info(f"  ✓ Image: {len(image_emb)}-dim")
            
            # Serialize embeddings to bytes
            text_emb_bytes = pickle.dumps(text_emb)
            image_emb_bytes = pickle.dumps(image_emb)
            
            # Create post
            post = Post(
                id=photo_id,
                content=content,
                media_url=row.get('photo_url', ''),
                author_id="photo_admin",
                author_name=row.get('photographer_username', 'photographer'),
                text_embedding=text_emb_bytes,
                image_embedding=image_emb_bytes,
                has_image=True,
                likes=max(1, int(row.get('stats_views', 0) or 0) // 1000),
                comments=max(1, int(row.get('stats_downloads', 0) or 0) // 50),
                created_at=datetime.utcnow()
            )
            
            # Save
            self.db.add(post)
            self.db.commit()
            
            logger.info(f"  ✅ Saved to database")
            self.stats['loaded'] += 1
            return True
            
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"  ⚠ Integrity error: {photo_id}")
            self.stats['skipped'] += 1
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"  ✗ Error: {e}")
            self.stats['failed'] += 1
            return False
    
    def load_all(self) -> None:
        """Load all images"""
        logger.info("=" * 70)
        logger.info("🖼  IMAGE DATA LOADER - MULTIMODAL CLIP SYSTEM")
        logger.info("=" * 70 + "\n")
        
        # Create tables
        logger.info("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tables created\n")
        
        # Read CSV
        csv_data = self.read_csv()
        if not csv_data:
            logger.error("No data to load")
            return
        
        self.stats['total'] = len(csv_data)
        
        # Load images
        logger.info(f"📥 Loading {len(csv_data)} images...\n")
        start_time = time.time()
        
        for idx, row in enumerate(csv_data, 1):
            photo_id = row.get('photo_id', '').strip()
            logger.info(f"\n[{idx}/{len(csv_data)}] Processing: {photo_id}")
            self.load_image(row)
        
        elapsed = time.time() - start_time
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ LOADING COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Total:     {self.stats['total']}")
        logger.info(f"Loaded:    {self.stats['loaded']} ✅")
        logger.info(f"Skipped:   {self.stats['skipped']} ℹ")
        logger.info(f"No image:  {self.stats['no_image']} ⚠")
        logger.info(f"Failed:    {self.stats['failed']} ✗")
        logger.info(f"Time:      {elapsed:.1f}s ({elapsed/len(csv_data):.1f}s per image)")
        logger.info(f"{'='*70}\n")
        
        self.db.close()

def main():
    backend_dir = Path(__file__).parent.parent
    csv_path = backend_dir / "data" / "images" / "metadata.csv"
    image_dir = backend_dir / "data" / "images"
    
    if not csv_path.exists():
        logger.error(f"✗ CSV not found: {csv_path}")
        return
    
    if not image_dir.exists():
        logger.error(f"✗ Image directory not found: {image_dir}")
        return
    
    logger.info(f"📁 CSV:    {csv_path}")
    logger.info(f"📁 Images: {image_dir}\n")
    
    loader = ImageLoader(str(csv_path), str(image_dir))
    loader.load_all()

if __name__ == "__main__":
    main()