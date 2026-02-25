#!/usr/bin/env python3
"""
Backend Configuration & Optimization Settings
Configure recommendation system parameters for your use case
"""
import json
from typing import Dict, Any, Optional

class RecommendationConfig:
    """Configuration for the recommendation system"""
    
    # ========== FAISS INDEX SETTINGS ==========
    FAISS_SETTINGS = {
        "index_type": "IVF",  # "Flat" for <10k items, "IVF" for >10k items
        "metric": "cosine",  # Distance metric for similarity
        "n_clusters": 100,  # For IVF index (use 2^(log2(n)/10))
        "nprobe": 20,  # Number of clusters to search (increase for accuracy, decrease for speed)
        "batch_size": 1000,  # Items per batch when building index
        "embedding_dimension": 384,  # all-MiniLM-L6-v2 model dimension
    }
    
    # ========== CACHING SETTINGS ==========
    CACHE_SETTINGS = {
        "embedding_cache_size": 1000,  # Max embeddings to cache in memory
        "search_cache_size": 500,  # Max search results to cache
        "cache_ttl_seconds": 3600,  # Time to live for cached items
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
    }
    
    # ========== BEHAVIOR ANALYSIS SETTINGS ==========
    BEHAVIOR_SETTINGS = {
        "interaction_decay_per_day": 0.95,  # How much weight to give old interactions
        "behavior_window_days": 30,  # Historical window for analysis
        "min_interactions_for_analysis": 3,  # Minimum interactions required
        "recency_weight": 0.3,  # Weight for recent interactions
        "frequency_weight": 0.25,  # Weight for frequency
        "velocity_weight": 0.25,  # Weight for interaction velocity
        "freshness_weight": 0.1,  # Weight for fresh content
    }
    
    # ========== RECOMMENDATION WEIGHTING ==========
    RECOMMENDATION_WEIGHTS = {
        "content_similarity": 0.4,  # Embedding similarity to liked content
        "user_preference": 0.3,  # Match with learned preferences
        "engagement_level": 0.2,  # Popularity/engagement metrics
        "freshness": 0.1,  # Recently posted content
    }
    
    # ========== DIVERSITY & FRESHNESS SETTINGS ==========
    DIVERSITY_SETTINGS = {
        "max_same_author": 0.3,  # Max % of results from same author
        "max_same_category": 0.4,  # Max % of results from same category
        "diversity_penalty": 0.85,  # Penalty multiplier for duplicate dimensions
        "freshness_halflife_days": 7,  # How fast content becomes "stale"
    }
    
    # ========== QUALITY MONITORING SETTINGS ==========
    QUALITY_SETTINGS = {
        "quality_threshold": 0.6,  # Minimum acceptable quality score
        "ctr_weight": 0.3,  # Weight for click-through rate
        "diversity_weight": 0.2,  # Weight for diversity score
        "relevance_weight": 0.35,  # Weight for relevance
        "novelty_weight": 0.15,  # Weight for novelty
    }
    
    # ========== ANOMALY DETECTION SETTINGS ==========
    ANOMALY_SETTINGS = {
        "session_threshold_seconds": 3600,  # Consider new session after this duration
        "max_interactions_per_hour": 50,  # Flag if user exceeds this
        "bot_confidence_threshold": 0.66,  # Confidence threshold for bot detection
        "stale_content_days": 30,  # Content older than this is "stale"
    }
    
    # ========== PERFORMANCE TUNING ==========
    PERFORMANCE_SETTINGS = {
        "max_index_size": 100000,  # Maximum items in index
        "reindex_frequency_hours": 24,  # How often to rebuild index
        "memory_optimization": True,  # Enable memory optimization
        "parallel_search": True,  # Use parallel search for large datasets
        "num_workers": 4,  # Number of worker processes
    }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Dict[str, Any]]:
        """Convert all settings to dictionary"""
        return {
            "faiss": cls.FAISS_SETTINGS,
            "cache": cls.CACHE_SETTINGS,
            "behavior": cls.BEHAVIOR_SETTINGS,
            "recommendations": cls.RECOMMENDATION_WEIGHTS,
            "diversity": cls.DIVERSITY_SETTINGS,
            "quality": cls.QUALITY_SETTINGS,
            "anomalies": cls.ANOMALY_SETTINGS,
            "performance": cls.PERFORMANCE_SETTINGS,
        }
    
    @classmethod
    def for_small_dataset(cls) -> Dict[str, Dict[str, Any]]:
        """Config optimized for small datasets (<1000 items)"""
        config = cls.to_dict()
        config["faiss"]["index_type"] = "Flat"  # No clustering for small datasets
        config["cache"]["embedding_cache_size"] = 500
        config["cache"]["cache_ttl_seconds"] = 7200  # Longer cache TTL
        config["performance"]["parallel_search"] = False
        return config
    
    @classmethod
    def for_medium_dataset(cls) -> Dict[str, Dict[str, Any]]:
        """Config optimized for medium datasets (1k-50k items)"""
        config = cls.to_dict()
        config["faiss"]["index_type"] = "IVF"
        config["faiss"]["n_clusters"] = 50
        config["cache"]["embedding_cache_size"] = 2000
        config["performance"]["num_workers"] = 4
        return config
    
    @classmethod
    def for_large_dataset(cls) -> Dict[str, Dict[str, Any]]:
        """Config optimized for large datasets (>50k items)"""
        config = cls.to_dict()
        config["faiss"]["index_type"] = "IVF"
        config["faiss"]["n_clusters"] = 200
        config["faiss"]["nprobe"] = 30
        config["cache"]["embedding_cache_size"] = 5000
        config["performance"]["num_workers"] = 8
        config["performance"]["parallel_search"] = True
        return config
    
    @classmethod
    def for_quality_focus(cls) -> Dict[str, Dict[str, Any]]:
        """Config optimized for recommendation quality"""
        config = cls.to_dict()
        config["faiss"]["nprobe"] = 50  # Search more clusters
        config["recommendations"]["content_similarity"] = 0.5
        config["recommendations"]["user_preference"] = 0.35
        config["recommendations"]["engagement_level"] = 0.1
        config["recommendations"]["freshness"] = 0.05
        config["diversity"]["diversity_penalty"] = 0.9  # Stricter diversity
        return config
    
    @classmethod
    def for_speed_focus(cls) -> Dict[str, Dict[str, Any]]:
        """Config optimized for response speed"""
        config = cls.to_dict()
        config["faiss"]["nprobe"] = 10  # Search fewer clusters
        config["cache"]["cache_ttl_seconds"] = 7200  # Longer cache
        config["behavior"]["behavior_window_days"] = 14  # Shorter history window
        config["performance"]["parallel_search"] = True
        return config


class OptimizationGuide:
    """Guide for optimizing the recommendation system"""
    
    RECOMMENDATIONS = {
        "small_dataset": {
            "description": "For datasets with <1,000 posts",
            "faiss_index": "Flat (exact search)",
            "cache_size": "Small (500-1000 items)",
            "reindex_frequency": "Daily or on demand",
            "expected_latency": "10-20ms",
            "expected_quality": "0.75-0.85",
        },
        "medium_dataset": {
            "description": "For datasets with 1K-50K posts",
            "faiss_index": "IVF (approximate search with 50-100 clusters)",
            "cache_size": "Medium (2000-5000 items)",
            "reindex_frequency": "Every 12-24 hours",
            "expected_latency": "15-50ms",
            "expected_quality": "0.70-0.80",
        },
        "large_dataset": {
            "description": "For datasets with >50K posts",
            "faiss_index": "IVF (approximate search with 200+ clusters)",
            "cache_size": "Large (5000-10000 items)",
            "reindex_frequency": "Every 6-12 hours",
            "expected_latency": "20-100ms",
            "expected_quality": "0.65-0.75",
        },
    }
    
    TUNING_PARAMETERS = {
        "low_latency_requirement": {
            "description": "Optimize for <50ms response time",
            "changes": {
                "nprobe": 10,  # Search fewer clusters
                "cache_ttl": 7200,  # Longer caching
                "batch_processing": True,
            }
        },
        "high_quality_requirement": {
            "description": "Optimize for >0.75 quality score",
            "changes": {
                "nprobe": 50,  # Search more clusters
                "diversity_boost": 0.8,  # Encourage diversity
                "min_similarity": 0.5,  # Filter low-quality results
            }
        },
        "high_concurrency": {
            "description": "Optimize for many concurrent requests",
            "changes": {
                "num_workers": 8,  # More parallel workers
                "batch_processing": True,
                "cache_aggressively": True,
            }
        },
        "memory_constrained": {
            "description": "Optimize for limited RAM (< 4GB)",
            "changes": {
                "embedding_cache_size": 500,
                "search_cache_size": 250,
                "batch_size": 500,  # Smaller batches
            }
        },
    }


def save_config(filename: str, config: Dict[str, Dict[str, Any]]) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Configuration saved to {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to save configuration: {e}")
        return False


def load_config(filename: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """Load configuration from JSON file"""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        print(f"✓ Configuration loaded from {filename}")
        return config
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return None


def print_config_summary():
    """Print summary of configuration options"""
    print("\n" + "="*70)
    print("RECOMMENDATION SYSTEM CONFIGURATION GUIDE")
    print("="*70)
    
    print("\n1. DATASET SIZE RECOMMENDATIONS:")
    for size, details in OptimizationGuide.RECOMMENDATIONS.items():
        print(f"\n   {size.upper()}:")
        for key, value in details.items():
            print(f"   - {key}: {value}")
    
    print("\n2. PERFORMANCE TUNING OPTIONS:")
    for scenario, details in OptimizationGuide.TUNING_PARAMETERS.items():
        print(f"\n   {scenario.upper()}:")
        print(f"   Description: {details['description']}")
        print(f"   Changes:")
        for param, value in details['changes'].items():
            print(f"   - {param}: {value}")
    
    print("\n3. CONFIGURATION FILES:")
    print("   Save and load configurations with:")
    print("   - save_config('my_config.json', config_dict)")
    print("   - load_config('my_config.json')")
    
    print("\n4. DEFAULT CONFIGURATIONS:")
    print("   - RecommendationConfig.for_small_dataset()")
    print("   - RecommendationConfig.for_medium_dataset()")
    print("   - RecommendationConfig.for_large_dataset()")
    print("   - RecommendationConfig.for_quality_focus()")
    print("   - RecommendationConfig.for_speed_focus()")


if __name__ == "__main__":
    # Print configuration guide
    print_config_summary()
    
    # Save example configurations
    small_config = RecommendationConfig.for_small_dataset()
    save_config("config_small_dataset.json", small_config)
    
    medium_config = RecommendationConfig.for_medium_dataset()
    save_config("config_medium_dataset.json", medium_config)
    
    large_config = RecommendationConfig.for_large_dataset()
    save_config("config_large_dataset.json", large_config)
    
    print("\n✓ Configuration files saved successfully!")
    print("  - config_small_dataset.json")
    print("  - config_medium_dataset.json")
    print("  - config_large_dataset.json")
