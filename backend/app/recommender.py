"""
FAISS-based recommendation engine with Sentence Transformers
Enhanced with robustness, caching, and advanced ranking
"""
import faiss
import numpy as np
import os
import pickle
import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from core.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH, TOP_K_RECOMMENDATIONS, EMBEDDING_DIMENSION
from app.embeddings import get_embedder

logger = logging.getLogger(__name__)

# Performance tracking
class PerformanceMetrics:
    """Track recommendation performance metrics"""
    def __init__(self):
        self.search_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_recommendations = 0
        self.avg_search_time = 0
    
    def record_search(self, time_ms: float):
        self.search_times.append(time_ms)
        self.avg_search_time = np.mean(self.search_times[-100:]) if self.search_times else 0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'avg_search_time_ms': round(self.avg_search_time, 2),
            'cache_hit_rate': self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
            'total_recommendations': self.total_recommendations
        }

class FAISSRecommender:
    def __init__(self):
        """Initialize FAISS recommender with enhanced features"""
        self.index = None
        self.metadata = {}
        self.embedder = get_embedder()
        self.metrics = PerformanceMetrics()
        self._embedding_cache = {}  # Cache embeddings for recently used items
        self._search_cache = {}  # Cache search results
        self._index_lock = False  # Prevent concurrent writes
        self.index_version = 0  # Track index updates
        self._load()

    def _load(self):
        """Load index and metadata from disk with validation"""
        if os.path.exists(FAISS_INDEX_PATH):
            try:
                self.index = faiss.read_index(FAISS_INDEX_PATH)
                logger.info(f"✓ Loaded FAISS index from {FAISS_INDEX_PATH}")
                logger.info(f"  Total vectors: {self.index.ntotal}, Dimension: {self.index.d}")
            except Exception as e:
                logger.error(f"✗ Failed to load FAISS index: {e}")
                self.index = None

        if os.path.exists(FAISS_METADATA_PATH):
            try:
                with open(FAISS_METADATA_PATH, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"✓ Loaded metadata with {len(self.metadata)} items")
            except Exception as e:
                logger.error(f"✗ Failed to load metadata: {e}")
                self.metadata = {}

    def build_index(self, embeddings: np.ndarray):
        """Build FAISS index from embeddings with optimization"""
        try:
            dim = embeddings.shape[1]
            n_samples = embeddings.shape[0]
            
            # Use more efficient indexing for larger datasets
            if n_samples > 10000:
                # Use IVF index for faster search on large datasets
                quantizer = faiss.IndexFlatL2(dim)
                n_clusters = min(100, n_samples // 39)
                self.index = faiss.IndexIVFFlat(quantizer, dim, n_clusters)
                self.index.train(embeddings.astype(np.float32))
                logger.info(f"Built IVF index with {n_clusters} clusters")
            else:
                # Use standard flat index for smaller datasets
                self.index = faiss.IndexFlatL2(dim)
            
            self.index.add(embeddings.astype(np.float32))
            logger.info(f"✓ Built FAISS index: {n_samples} vectors, dimension {dim}")
            self.index_version += 1
        except Exception as e:
            logger.error(f"✗ Failed to build index: {e}")
            raise

    def save(self):
        """Save index and metadata to disk with integrity checks"""
        try:
            if not self.index or self.index.ntotal == 0:
                logger.warning("⚠ Index is empty, skipping save")
                return
            
            os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
            
            # Atomic write: save to temp file first
            temp_index_path = FAISS_INDEX_PATH + '.tmp'
            temp_meta_path = FAISS_METADATA_PATH + '.tmp'
            
            faiss.write_index(self.index, temp_index_path)
            with open(temp_meta_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            # Atomic rename
            os.replace(temp_index_path, FAISS_INDEX_PATH)
            os.replace(temp_meta_path, FAISS_METADATA_PATH)
            
            logger.info(f"✓ Saved FAISS index ({self.index.ntotal} vectors) and metadata ({len(self.metadata)} items)")
        except Exception as e:
            logger.error(f"✗ Failed to save index: {e}")
            raise

    def add_items(self, items: List[Dict[str, Any]], rebuild: bool = False):
        """
        Add items to the index with deduplication and validation
        
        Args:
            items: List of dicts with 'id', 'content', and optional metadata
            rebuild: Whether to rebuild index from scratch
        """
        if self._index_lock:
            logger.warning("⚠ Index is locked, operation deferred")
            return
        
        try:
            if not items:
                return

            # Validate and filter items
            valid_items = []
            for item in items:
                if not item.get('id') or not item.get('content'):
                    logger.warning(f"⚠ Skipping invalid item: {item.get('id')}")
                    continue
                valid_items.append(item)
            
            if not valid_items:
                logger.warning("✗ No valid items to add")
                return

            # Check for duplicates
            existing_ids = {meta.get('id') for meta in self.metadata.values()}
            new_items = [item for item in valid_items if item.get('id') not in existing_ids]
            
            if not new_items:
                logger.info("ℹ All items already in index")
                return
            
            logger.info(f"Adding {len(new_items)} new items (skipped {len(valid_items) - len(new_items)} duplicates)")

            # Extract content and generate embeddings
            contents = [item.get('content', '') for item in new_items]
            embeddings = self.embedder.encode(contents)

            # Build or update index
            if self.index is None or rebuild:
                all_embeddings = embeddings
                self.metadata = {i: item for i, item in enumerate(new_items)}
                self.build_index(all_embeddings)
            else:
                self.index.add(embeddings.astype(np.float32))
                # Update metadata with new indices
                start_idx = len(self.metadata)
                for i, item in enumerate(new_items):
                    self.metadata[start_idx + i] = item

            self.save()
            self._search_cache.clear()  # Invalidate search cache
            logger.info(f"✓ Added {len(new_items)} items to index (total: {self.index.ntotal})")
        except Exception as e:
            logger.error(f"✗ Failed to add items: {e}")
            raise

    def search_multimodal(self, query_text: str = None, query_image_embedding: np.ndarray = None, 
                         k: int = TOP_K_RECOMMENDATIONS, text_weight: float = 0.5, 
                         image_weight: float = 0.5) -> List[Dict[str, Any]]:
        """
        Multimodal search using both text and image embeddings
        
        Args:
            query_text: Text query (uses text encoder)
            query_image_embedding: Pre-computed image embedding (512-dim from CLIP)
            k: Number of results
            text_weight: Weight for text similarity (0-1)
            image_weight: Weight for image similarity (0-1)
            
        Returns:
            List of ranked items with multimodal scores
        """
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("⚠ Index is empty")
                return []
            
            results = []
            
            # Get text similarity scores if text query provided
            text_scores = {}
            if query_text:
                text_results = self.search(query_text, k=k*2, diversity_boost=0.0)
                for idx, item in enumerate(text_results):
                    text_scores[item['id']] = item.get('similarity_score', 0.0)
            
            # Get image similarity scores if image embedding provided
            image_scores = {}
            if query_image_embedding is not None:
                # Check if we have image embeddings stored
                if not hasattr(self, '_post_embeddings'):
                    self._post_embeddings = {}
                
                # Compute image similarity to all posts
                for post_id, metadata_dict in self.metadata.items():
                    if post_id in self._post_embeddings and self._post_embeddings[post_id].get('image_embedding') is not None:
                        img_emb = self._post_embeddings[post_id]['image_embedding']
                        # Cosine similarity for image embeddings
                        similarity = np.dot(query_image_embedding, img_emb) / (np.linalg.norm(query_image_embedding) * np.linalg.norm(img_emb) + 1e-8)
                        image_scores[metadata_dict.get('id', post_id)] = float(similarity)
            
            # Combine scores
            seen_ids = set()
            for item_idx, metadata_dict in self.metadata.items():
                item_id = metadata_dict.get('id', str(item_idx))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                
                # Get component scores
                text_sim = text_scores.get(item_id, 0.0)
                image_sim = image_scores.get(item_id, 0.0)
                
                # Compute weighted multimodal score
                multimodal_score = (text_sim * text_weight + image_sim * image_weight) / (text_weight + image_weight) if (text_weight + image_weight) > 0 else 0.0
                
                # Only include if either text or image match exists
                if multimodal_score > 0:
                    item = metadata_dict.copy()
                    item['text_similarity_score'] = float(text_sim)
                    item['image_similarity_score'] = float(image_sim)
                    item['multimodal_score'] = float(multimodal_score)
                    results.append(item)
            
            # Sort by multimodal score
            results.sort(key=lambda x: x.get('multimodal_score', 0), reverse=True)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Multimodal search failed: {e}")
            return []

    def search(self, query: str, k: int = TOP_K_RECOMMENDATIONS, 
               diversity_boost: float = 0.0, freshness_weight: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar items with advanced ranking
        
        Args:
            query: Query text
            k: Number of results to return
            diversity_boost: Boost diversity in results (0-1)
            freshness_weight: Weight recent items higher (0-1)
            
        Returns:
            List of similar items with distances and scores
        """
        import time
        start_time = time.time()
        
        try:
            if self.index is None or self.index.ntotal == 0:
                logger.warning("⚠ Index is empty")
                return []

            # Check cache
            cache_key = f"{query}:{k}:{diversity_boost}:{freshness_weight}"
            if cache_key in self._search_cache:
                self.metrics.cache_hits += 1
                logger.debug("Cache hit for query")
                return self._search_cache[cache_key]
            
            self.metrics.cache_misses += 1

            # Generate query embedding (with caching)
            if query not in self._embedding_cache:
                self._embedding_cache[query] = self.embedder.encode_single(query)
            query_embedding = np.array([self._embedding_cache[query]]).astype(np.float32)

            # Search with safety margin for diversity
            search_k = min(k * 3 if diversity_boost > 0 else k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, search_k)

            # Format and rank results
            results = []
            selected_indices = set()
            
            for idx, distance in zip(indices[0], distances[0]):
                idx = int(idx)
                if idx not in self.metadata:
                    continue
                
                item = self.metadata[idx].copy()
                similarity = self._distance_to_similarity(float(distance))
                
                # Apply freshness boost if applicable
                if freshness_weight > 0:
                    freshness_score = self._calculate_freshness_score(item)
                    similarity = similarity * (1 - freshness_weight) + freshness_score * freshness_weight
                
                # Apply diversity penalties
                if diversity_boost > 0 and len(results) > 0:
                    diversity_penalty = self._calculate_diversity_penalty(item, results, diversity_boost)
                    similarity *= (1 - diversity_penalty)
                
                item['distance'] = float(distance)
                item['similarity_score'] = float(similarity)
                results.append(item)
                selected_indices.add(idx)
                
                if len(results) >= k:
                    break
            
            # Sort by final score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            results = results[:k]
            
            # Cache results
            self._search_cache[cache_key] = results
            
            # Record metrics
            elapsed = (time.time() - start_time) * 1000
            self.metrics.record_search(elapsed)
            self.metrics.total_recommendations += 1
            
            logger.debug(f"Found {len(results)} results in {elapsed:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"✗ Search failed: {e}")
            return []

    def _distance_to_similarity(self, distance: float) -> float:
        """Convert L2 distance to similarity score (0-1)"""
        # Using exponential decay for smoother similarity scores
        return np.exp(-distance / 10.0)
    
    def _calculate_freshness_score(self, item: Dict[str, Any]) -> float:
        """Calculate freshness score based on creation time"""
        try:
            created_at = item.get('created_at')
            if not created_at:
                return 0.5
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            days_old = (datetime.utcnow() - created_at).days
            # Decay with 30-day half-life
            return np.exp(-days_old / 30.0)
        except Exception:
            return 0.5
    
    def _calculate_diversity_penalty(self, item: Dict[str, Any], 
                                    selected: List[Dict[str, Any]], 
                                    diversity_boost: float) -> float:
        """Calculate diversity penalty based on similarity to already selected items"""
        penalty = 0.0
        for selected_item in selected:
            if item.get('id') == selected_item.get('id'):
                return 1.0  # Already selected
            
            # Check category/author similarity
            if item.get('author') == selected_item.get('author'):
                penalty = max(penalty, 0.3 * diversity_boost)
            if item.get('category') == selected_item.get('category'):
                penalty = max(penalty, 0.5 * diversity_boost)
        
        return penalty

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed index and performance statistics"""
        if self.index is None:
            return {
                'total_items': 0,
                'dimension': 0,
                'metadata_count': 0,
                'performance': {'avg_search_time_ms': 0, 'cache_hit_rate': 0, 'total_recommendations': 0}
            }
        
        return {
            'total_items': self.index.ntotal,
            'dimension': self.index.d,
            'metadata_count': len(self.metadata),
            'index_version': self.index_version,
            'cache_size': len(self._embedding_cache),
            'search_cache_size': len(self._search_cache),
            'performance': self.metrics.get_stats()
        }
    
    def clear_caches(self):
        """Clear internal caches to free memory"""
        self._embedding_cache.clear()
        self._search_cache.clear()
        logger.info("✓ Cleared all caches")
    
    def reindex(self, rebuild: bool = True):
        """Rebuild index from existing metadata (useful for optimization)"""
        try:
            if not self.metadata:
                logger.warning("⚠ No metadata to reindex")
                return
            
            logger.info(f"Reindexing {len(self.metadata)} items...")
            contents = [self.metadata[i].get('content', '') for i in sorted(self.metadata.keys())]
            embeddings = self.embedder.encode(contents)
            self.build_index(embeddings)
            self.save()
            logger.info("✓ Reindex complete")
        except Exception as e:
            logger.error(f"✗ Reindex failed: {e}")
            raise


# Global recommender instance
_recommender = None

def get_recommender() -> FAISSRecommender:
    """Get or create global recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = FAISSRecommender()
    return _recommender

