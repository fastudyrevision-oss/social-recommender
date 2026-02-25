"""
Comprehensive integration tests for enhanced backend recommendation system
Tests hybrid recommendations, advanced caching, time-decay, and collaborative filtering
"""
import asyncio
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:8000"

# Test data with varied content types
DIVERSE_POSTS = [
    {
        "id": "travel_1",
        "content": "Exploring the temples of Bali, Indonesia. Incredible architecture and culture!",
        "author": "travel_guru",
        "likes": 234,
        "comments": 45,
        "shares": 78,
        "metadata": {"category": "travel", "tags": ["bali", "temples", "asia"], "length": "medium"}
    },
    {
        "id": "tech_1",
        "content": "New breakthrough in quantum computing could revolutionize cryptography. Major implications.",
        "author": "quantum_researcher",
        "likes": 567,
        "comments": 89,
        "shares": 123,
        "metadata": {"category": "technology", "tags": ["quantum", "computing", "crypto"], "length": "short"}
    },
    {
        "id": "food_1",
        "content": "Made homemade pasta from scratch. Tried a traditional carbonara recipe from Rome. Perfetto!",
        "author": "food_blogger",
        "likes": 345,
        "comments": 67,
        "shares": 89,
        "metadata": {"category": "food", "tags": ["cooking", "pasta", "italian"], "length": "medium"}
    },
    {
        "id": "fitness_1",
        "content": "Completed my first marathon! 42.2km of pure determination. So proud of the journey!",
        "author": "fitness_advocate",
        "likes": 456,
        "comments": 78,
        "shares": 123,
        "metadata": {"category": "fitness", "tags": ["marathon", "running", "achievement"], "length": "short"}
    },
    {
        "id": "art_1",
        "content": "Spent 6 months creating this digital painting. Abstract expressionism exploring emotion and color.",
        "author": "digital_artist",
        "likes": 289,
        "comments": 45,
        "shares": 67,
        "metadata": {"category": "art", "tags": ["digital", "painting", "abstract"], "length": "short"}
    },
    {
        "id": "tech_2",
        "content": "Building a machine learning model with TensorFlow. Achieving 96% accuracy on validation set!",
        "author": "ml_engineer",
        "likes": 412,
        "comments": 56,
        "shares": 89,
        "metadata": {"category": "technology", "tags": ["ml", "tensorflow", "ai"], "length": "medium"}
    },
    {
        "id": "travel_2",
        "content": "Road trip through Iceland with minimal plans. Best spontaneous decision ever!",
        "author": "adventure_seeker",
        "likes": 523,
        "comments": 92,
        "shares": 145,
        "metadata": {"category": "travel", "tags": ["iceland", "roadtrip", "adventure"], "length": "short"}
    },
    {
        "id": "food_2",
        "content": "Michelin star restaurant experience. The tasting menu was an unforgettable journey of flavors.",
        "author": "foodie_critic",
        "likes": 378,
        "comments": 63,
        "shares": 98,
        "metadata": {"category": "food", "tags": ["michelin", "dining", "gourmet"], "length": "medium"}
    },
]

USERS = ["user_travel", "user_tech", "user_fitness", "user_art", "user_balanced"]

INTERACTION_PATTERNS = [
    {"user_id": "user_travel", "post_id": "travel_1", "interaction_type": "like", "timestamp": datetime.now()},
    {"user_id": "user_travel", "post_id": "travel_2", "interaction_type": "like", "timestamp": datetime.now()},
    {"user_id": "user_tech", "post_id": "tech_1", "interaction_type": "view", "timestamp": datetime.now() - timedelta(hours=1)},
    {"user_id": "user_tech", "post_id": "tech_2", "interaction_type": "comment", "timestamp": datetime.now() - timedelta(hours=2)},
    {"user_id": "user_fitness", "post_id": "fitness_1", "interaction_type": "share", "timestamp": datetime.now() - timedelta(days=1)},
    {"user_id": "user_art", "post_id": "art_1", "interaction_type": "bookmark", "timestamp": datetime.now() - timedelta(hours=3)},
    {"user_id": "user_balanced", "post_id": "travel_1", "interaction_type": "like", "timestamp": datetime.now() - timedelta(days=2)},
    {"user_id": "user_balanced", "post_id": "tech_1", "interaction_type": "view", "timestamp": datetime.now() - timedelta(days=1)},
    {"user_id": "user_balanced", "post_id": "food_1", "interaction_type": "like", "timestamp": datetime.now()},
]


def test_basic_connectivity():
    """Test basic API connectivity"""
    print("\n" + "="*60)
    print("TEST 1: Basic API Connectivity")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"✓ API Health: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ API Connection Failed: {e}")
        return False


def test_add_posts():
    """Test adding posts to the system"""
    print("\n" + "="*60)
    print("TEST 2: Add Posts to System")
    print("="*60)
    
    try:
        response = requests.post(f"{API_BASE_URL}/posts/batch", json={"posts": DIVERSE_POSTS})
        result = response.json()
        print(f"✓ Added {result.get('count', 0)} posts")
        print(f"  Status: {result.get('status', 'unknown')}")
        return True
    except Exception as e:
        print(f"✗ Failed to add posts: {e}")
        return False


def test_track_interactions():
    """Test tracking user interactions"""
    print("\n" + "="*60)
    print("TEST 3: Track User Interactions")
    print("="*60)
    
    success_count = 0
    try:
        for interaction in INTERACTION_PATTERNS:
            response = requests.post(f"{API_BASE_URL}/track/interaction", json=interaction)
            if response.status_code == 200:
                success_count += 1
        
        print(f"✓ Tracked {success_count}/{len(INTERACTION_PATTERNS)} interactions")
        return success_count > 0
    except Exception as e:
        print(f"✗ Failed to track interactions: {e}")
        return False


def test_user_preferences():
    """Test user preference inference"""
    print("\n" + "="*60)
    print("TEST 4: User Preference Inference")
    print("="*60)
    
    try:
        for user_id in USERS[:2]:  # Test first 2 users
            response = requests.get(f"{API_BASE_URL}/user/{user_id}/preferences")
            if response.status_code == 200:
                prefs = response.json().get("preferences", {})
                print(f"\n✓ User: {user_id}")
                print(f"  Categories: {list(prefs.get('category_preferences', {}).keys())[:3]}")
                print(f"  Top Tags: {prefs.get('top_tags', [])[:3]}")
                print(f"  Engagement Level: {prefs.get('engagement_level', 'unknown')}")
    except Exception as e:
        print(f"✗ Failed to get preferences: {e}")
        return False
    
    return True


def test_personalized_recommendations():
    """Test personalized hybrid recommendations"""
    print("\n" + "="*60)
    print("TEST 5: Personalized Hybrid Recommendations")
    print("="*60)
    
    try:
        test_user = "user_tech"
        response = requests.post(f"{API_BASE_URL}/recommendations/personalized", json={
            "user_id": test_user,
            "top_k": 5
        })
        
        if response.status_code == 200:
            result = response.json()
            recs = result.get("recommendations", [])
            print(f"\n✓ Generated {len(recs)} recommendations for {test_user}")
            
            for i, rec in enumerate(recs[:3], 1):
                print(f"\n  Recommendation {i}:")
                print(f"    Post ID: {rec.get('id', 'unknown')}")
                print(f"    Author: {rec.get('author', 'unknown')}")
                print(f"    Category: {rec.get('category', 'unknown')}")
                print(f"    Engagement Score: {rec.get('engagement_score', 0):.2f}")
                print(f"    Reason: {rec.get('recommendation_reason', 'hybrid match')}")
            
            return True
    except Exception as e:
        print(f"✗ Failed to get personalized recommendations: {e}")
        return False


def test_advanced_recommendations():
    """Test advanced recommendations with diversity and freshness"""
    print("\n" + "="*60)
    print("TEST 6: Advanced Recommendations (Diversity & Freshness)")
    print("="*60)
    
    try:
        test_user = "user_balanced"
        
        # Test with diversity boost
        response = requests.post(f"{API_BASE_URL}/recommend/advanced", json={
            "user_id": test_user,
            "top_k": 4,
            "diversity_boost": 0.7,
            "freshness_weight": 0.3
        })
        
        if response.status_code == 200:
            result = response.json()
            recs = result.get("recommendations", [])
            
            print(f"\n✓ Generated {len(recs)} advanced recommendations for {test_user}")
            print(f"  Parameters: diversity={result.get('parameters', {}).get('diversity_boost', 0)}, freshness={result.get('parameters', {}).get('freshness_weight', 0)}")
            
            # Check diversity
            authors = [rec.get('author') for rec in recs]
            unique_authors = len(set(authors))
            print(f"  Author Diversity: {unique_authors}/{len(recs)} unique authors")
            
            return True
    except Exception as e:
        print(f"✗ Failed to get advanced recommendations: {e}")
        return False


def test_user_insights():
    """Test comprehensive user insights"""
    print("\n" + "="*60)
    print("TEST 7: User Insights & Analytics")
    print("="*60)
    
    try:
        test_user = "user_balanced"
        response = requests.get(f"{API_BASE_URL}/user/{test_user}/insights")
        
        if response.status_code == 200:
            result = response.json()
            insights = result.get("insights", {})
            
            print(f"\n✓ Retrieved insights for {test_user}")
            print(f"  Total Interactions: {insights.get('total_interactions', 0)}")
            print(f"  Engagement Level: {insights.get('engagement_level', 'unknown')}")
            print(f"  Activity Status: {insights.get('activity_status', 'unknown')}")
            print(f"  Favorite Categories: {insights.get('top_categories', [])[:3]}")
            
            if 'predictions' in insights:
                print(f"\n  Predictions:")
                pred = insights['predictions']
                print(f"    Next Interaction: {pred.get('predicted_interaction_type', 'unknown')}")
                print(f"    Timing (minutes): {pred.get('time_until_next_minutes', 'unknown')}")
                print(f"    Confidence: {pred.get('confidence', 0):.2f}")
            
            return True
    except Exception as e:
        print(f"✗ Failed to get insights: {e}")
        return False


def test_performance_metrics():
    """Test performance monitoring endpoints"""
    print("\n" + "="*60)
    print("TEST 8: Performance Metrics & Diagnostics")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/diagnostics/performance")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Performance Metrics Retrieved")
            
            # Recommender stats
            rec_stats = result.get("recommender", {})
            print(f"\n  Recommender Stats:")
            print(f"    Total Posts: {rec_stats.get('total_items', 0)}")
            print(f"    Index Type: {rec_stats.get('index_type', 'unknown')}")
            print(f"    Embedding Dimension: {rec_stats.get('embedding_dim', 0)}")
            
            # Performance metrics
            perf = result.get("performance", {})
            print(f"\n  Performance Metrics:")
            print(f"    Avg Search Time: {perf.get('avg_search_time_ms', 0):.2f}ms")
            print(f"    Cache Hit Rate: {perf.get('cache_hit_rate', 0):.2%}")
            print(f"    Total Recommendations: {perf.get('total_recommendations', 0)}")
            
            # System stats
            print(f"\n  System Stats:")
            print(f"    Users Tracked: {result.get('users_tracked', 0)}")
            print(f"    Total Interactions: {result.get('total_interactions', 0)}")
            
            return True
    except Exception as e:
        print(f"✗ Failed to get performance metrics: {e}")
        return False


def test_cache_operations():
    """Test cache management endpoints"""
    print("\n" + "="*60)
    print("TEST 9: Cache Management Operations")
    print("="*60)
    
    try:
        # Generate some cache hits first
        user_id = "user_tech"
        for _ in range(2):
            requests.post(f"{API_BASE_URL}/recommendations/personalized", json={
                "user_id": user_id,
                "top_k": 5
            })
        
        # Clear caches
        response = requests.post(f"{API_BASE_URL}/optimize/clear-caches")
        if response.status_code == 200:
            print(f"✓ Caches cleared successfully")
            print(f"  Message: {response.json().get('message', '')}")
            return True
    except Exception as e:
        print(f"✗ Failed to clear caches: {e}")
        return False


def test_index_optimization():
    """Test index optimization endpoints"""
    print("\n" + "="*60)
    print("TEST 10: Index Optimization")
    print("="*60)
    
    try:
        response = requests.post(f"{API_BASE_URL}/optimize/reindex")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Index optimization completed")
            print(f"  Status: {result.get('status', 'unknown')}")
            
            stats = result.get("new_stats", {})
            print(f"\n  New Index Stats:")
            print(f"    Total Items: {stats.get('total_items', 0)}")
            print(f"    Index Version: {stats.get('index_version', 0)}")
            
            return True
    except Exception as e:
        print(f"✗ Failed to optimize index: {e}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("ENHANCED BACKEND RECOMMENDATION SYSTEM - INTEGRATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("API Connectivity", test_basic_connectivity),
        ("Add Posts", test_add_posts),
        ("Track Interactions", test_track_interactions),
        ("User Preferences", test_user_preferences),
        ("Personalized Recommendations", test_personalized_recommendations),
        ("Advanced Recommendations", test_advanced_recommendations),
        ("User Insights", test_user_insights),
        ("Performance Metrics", test_performance_metrics),
        ("Cache Operations", test_cache_operations),
        ("Index Optimization", test_index_optimization),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' encountered error: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed*100//total}%)")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
