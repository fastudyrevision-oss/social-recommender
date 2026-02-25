"""
Sample data generator for testing the recommender system
"""
import requests
import json
from typing import List

API_BASE_URL = "http://localhost:8000"

SAMPLE_POSTS = [
    {
        "id": "1",
        "content": "Just finished an amazing hiking trip in the mountains! The views were breathtaking.",
        "author": "nature_lover",
        "likes": 156,
        "comments": 23,
        "shares": 12,
        "metadata": {"category": "travel", "tags": ["hiking", "mountains", "nature"]}
    },
    {
        "id": "2",
        "content": "Machine learning is transforming how we solve problems. Excited about the future!",
        "author": "tech_enthusiast",
        "likes": 342,
        "comments": 67,
        "shares": 89,
        "metadata": {"category": "technology", "tags": ["AI", "ML", "tech"]}
    },
    {
        "id": "3",
        "content": "Sunset at the beach was absolutely perfect. Golden hour photography at its finest!",
        "author": "photography_pro",
        "likes": 567,
        "comments": 45,
        "shares": 234,
        "metadata": {"category": "photography", "tags": ["sunset", "beach", "photography"]}
    },
    {
        "id": "4",
        "content": "Learning Python has been a game-changer for my data science career. Best decision ever!",
        "author": "data_scientist",
        "likes": 223,
        "comments": 34,
        "shares": 45,
        "metadata": {"category": "education", "tags": ["python", "programming", "learning"]}
    },
    {
        "id": "5",
        "content": "Deep learning neural networks are incredibly powerful. Just trained my first CNN model!",
        "author": "ai_researcher",
        "likes": 189,
        "comments": 52,
        "shares": 78,
        "metadata": {"category": "technology", "tags": ["deeplearning", "neural networks", "AI"]}
    },
    {
        "id": "6",
        "content": "Exploring new mountain trails this weekend. Nothing beats the peace of nature.",
        "author": "adventure_seeker",
        "likes": 298,
        "comments": 29,
        "shares": 56,
        "metadata": {"category": "travel", "tags": ["mountains", "hiking", "adventure"]}
    },
    {
        "id": "7",
        "content": "Photography tips: Golden hour is your best friend. Capture the magic!",
        "author": "photo_tips",
        "likes": 412,
        "comments": 61,
        "shares": 123,
        "metadata": {"category": "photography", "tags": ["tips", "golden hour", "photography"]}
    },
    {
        "id": "8",
        "content": "Artificial intelligence and machine learning job market is booming right now.",
        "author": "career_coach",
        "likes": 334,
        "comments": 78,
        "shares": 145,
        "metadata": {"category": "career", "tags": ["jobs", "AI", "career"]}
    },
    {
        "id": "9",
        "content": "Beautiful forest walk with ancient trees. Nature's masterpiece!",
        "author": "nature_photographer",
        "likes": 445,
        "comments": 38,
        "shares": 89,
        "metadata": {"category": "nature", "tags": ["forest", "nature", "photography"]}
    },
    {
        "id": "10",
        "content": "Started learning computer vision with OpenCV. Fascinating field!",
        "author": "cv_researcher",
        "likes": 267,
        "comments": 44,
        "shares": 67,
        "metadata": {"category": "technology", "tags": ["computer vision", "opencv", "python"]}
    }
]

TEST_QUERIES = [
    "hiking and mountain adventures",
    "machine learning and artificial intelligence",
    "photography and sunset",
    "Python programming",
    "nature and beautiful landscapes",
    "deep learning neural networks",
]


def add_sample_data():
    """Add sample posts to the recommender"""
    print("Adding sample posts...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/posts/batch",
            json=SAMPLE_POSTS,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result['message']}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Failed to add posts: {e}")
        return False


def test_recommendations():
    """Test recommendation system"""
    print("\nTesting recommendations...")
    
    for query in TEST_QUERIES:
        try:
            response = requests.post(
                f"{API_BASE_URL}/recommend",
                json={"query": query, "top_k": 3},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nQuery: '{query}'")
                print(f"Cached: {result['cached']}")
                print("Recommendations:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec['author']}: {rec['content'][:50]}...")
                    print(f"     Similarity: {rec['similarity']:.2%}")
            else:
                print(f"✗ Error for query '{query}': {response.status_code}")
        except Exception as e:
            print(f"✗ Request failed: {e}")


def get_stats():
    """Get system statistics"""
    print("\nSystem Statistics:")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Total items: {stats['index_stats']['total_items']}")
            print(f"Dimension: {stats['index_stats']['dimension']}")
            print(f"Embedding model: {stats['embedding_model']}")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")


def main():
    """Main test flow"""
    print("=" * 60)
    print("Social Media Recommender - Test Script")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("✗ Server is not responding correctly")
            return
        print("✓ Server is running")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print(f"  Make sure the server is running on {API_BASE_URL}")
        return
    
    # Add sample data
    if not add_sample_data():
        return
    
    # Get statistics
    get_stats()
    
    # Test recommendations
    test_recommendations()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
