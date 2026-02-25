"""
Seed the database with sample posts for testing and recommendations
"""
import json
from uuid import uuid4
from datetime import datetime, timedelta
from app.recommender import get_recommender
from app.redis_cache import get_cache

# Get components
recommender = get_recommender()
cache = get_cache()

# Sample posts covering various categories
sample_posts = [
    {
        "id": str(uuid4()),
        "content": "Just launched my new machine learning project! Check out the GitHub repo for details on building semantic search with FAISS",
        "author": "alice_tech",
        "likes": 42,
        "comments": 8,
        "shares": 3,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Amazing sunset at the beach today! Nature photography is my passion 📸🌅",
        "author": "bob_photos",
        "likes": 156,
        "comments": 23,
        "shares": 12,
        "media_type": "image",
        "media_url": "https://example.com/sunset.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Just finished cooking an amazing Italian pasta dish! The key is fresh ingredients and patience 🍝👨‍🍳",
        "author": "chef_maria",
        "likes": 89,
        "comments": 15,
        "shares": 7,
        "media_type": "image",
        "media_url": "https://example.com/pasta.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Deep learning with transformers - a comprehensive guide. Learn about attention mechanisms and BERT models",
        "author": "dr_ai",
        "likes": 234,
        "comments": 45,
        "shares": 89,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Morning yoga session - Start your day with mindfulness and stretching! 🧘‍♀️✨",
        "author": "wellness_guru",
        "likes": 67,
        "comments": 12,
        "shares": 5,
        "media_type": "image",
        "media_url": "https://example.com/yoga.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Vector databases are revolutionizing how we build AI applications. FAISS, Pinecone, Weaviate explained",
        "author": "alice_tech",
        "likes": 178,
        "comments": 34,
        "shares": 56,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Golden hour photography tips - how to capture the perfect light during sunset 📷✨",
        "author": "bob_photos",
        "likes": 203,
        "comments": 41,
        "shares": 28,
        "media_type": "image",
        "media_url": "https://example.com/golden-hour.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Recipe: No-bake chocolate cheesecake - smooth, creamy, and absolutely delicious 🍰😋",
        "author": "chef_maria",
        "likes": 145,
        "comments": 28,
        "shares": 19,
        "media_type": "image",
        "media_url": "https://example.com/cheesecake.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Building a RAG system with LangChain and OpenAI - retrieval augmented generation explained with examples",
        "author": "dr_ai",
        "likes": 267,
        "comments": 52,
        "shares": 103,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Meditation for beginners - Simple techniques to reduce stress and improve mental health 🧠💆",
        "author": "wellness_guru",
        "likes": 112,
        "comments": 21,
        "shares": 14,
        "media_type": "image",
        "media_url": "https://example.com/meditation.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "The future of NLP: Large Language Models and their applications in business and research",
        "author": "dr_ai",
        "likes": 289,
        "comments": 67,
        "shares": 134,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Travel vlog: Exploring Tokyo's hidden gems and street food! 🗾🍜 Watch till the end for my favorite ramen shop",
        "author": "travel_vlogger",
        "likes": 298,
        "comments": 55,
        "shares": 42,
        "media_type": "video",
        "media_url": "https://example.com/tokyo-vlog.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "AI and ethics - Important considerations when deploying machine learning models in production",
        "author": "alice_tech",
        "likes": 156,
        "comments": 38,
        "shares": 67,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Landscape photography masterclass - composition, lighting, and post-processing techniques 📸🏔️",
        "author": "bob_photos",
        "likes": 187,
        "comments": 36,
        "shares": 44,
        "media_type": "image",
        "media_url": "https://example.com/landscape.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Homemade sourdough bread recipe - Learn how to make the perfect crust and crumb 🍞",
        "author": "chef_maria",
        "likes": 178,
        "comments": 42,
        "shares": 31,
        "media_type": "image",
        "media_url": "https://example.com/sourdough.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "High-intensity interval training (HIIT) - Get fit in 20 minutes! 💪🏃‍♂️",
        "author": "fitness_coach",
        "likes": 234,
        "comments": 48,
        "shares": 62,
        "media_type": "video",
        "media_url": "https://example.com/hiit-workout.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "Fine-tuning language models for your specific use case - Best practices and implementation guide",
        "author": "dr_ai",
        "likes": 312,
        "comments": 58,
        "shares": 145,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Urban photography: Capturing the essence of city life through my lens 🌃🏙️",
        "author": "bob_photos",
        "likes": 224,
        "comments": 39,
        "shares": 51,
        "media_type": "image",
        "media_url": "https://example.com/urban.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Vegan cooking: Delicious plant-based recipes that everyone will love 🌱🍲",
        "author": "chef_maria",
        "likes": 167,
        "comments": 34,
        "shares": 28,
        "media_type": "image",
        "media_url": "https://example.com/vegan.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Yoga flow for flexibility and strength - 30 minute routine perfect for all levels 🧘‍♀️🙏",
        "author": "wellness_guru",
        "likes": 198,
        "comments": 45,
        "shares": 67,
        "media_type": "video",
        "media_url": "https://example.com/yoga-flow.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "Machine learning is transforming how we solve problems. Excited about the future! #AI #ML #Tech",
        "author": "tech_enthusiast",
        "likes": 342,
        "comments": 67,
        "shares": 89,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Hiking the Pacific Coast Trail - Day 5 of my adventure! The views are incredible 🏔️⛰️",
        "author": "adventure_seeker",
        "likes": 267,
        "comments": 44,
        "shares": 38,
        "media_type": "image",
        "media_url": "https://example.com/hiking.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Breakfast bowl recipe - acai, granola, fresh berries, and coconut milk ✨🍓",
        "author": "healthy_eating",
        "likes": 198,
        "comments": 36,
        "shares": 28,
        "media_type": "image",
        "media_url": "https://example.com/bowl.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Web development tips: Using React hooks effectively - useState, useEffect, custom hooks explained",
        "author": "code_master",
        "likes": 445,
        "comments": 89,
        "shares": 156,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Sunrise over the mountains - Nature's way of reminding us it's a new day 🌅🏔️",
        "author": "nature_lover",
        "likes": 334,
        "comments": 67,
        "shares": 102,
        "media_type": "image",
        "media_url": "https://example.com/sunrise.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Stress management techniques: meditation, breathing exercises, and time management strategies",
        "author": "wellness_guru",
        "likes": 256,
        "comments": 54,
        "shares": 71,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Coffee roasting at home: From green beans to perfect espresso in your kitchen ☕",
        "author": "coffee_lover",
        "likes": 287,
        "comments": 52,
        "shares": 44,
        "media_type": "image",
        "media_url": "https://example.com/coffee.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Python data structures: Lists, dictionaries, sets, and tuples - when to use each one",
        "author": "code_master",
        "likes": 523,
        "comments": 112,
        "shares": 198,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Fashion inspiration: Summer outfit ideas for casual and professional settings 👗👔",
        "author": "style_blogger",
        "likes": 412,
        "comments": 78,
        "shares": 134,
        "media_type": "image",
        "media_url": "https://example.com/fashion.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Neural networks explained simply - perceptrons, backpropagation, and deep learning fundamentals",
        "author": "dr_ai",
        "likes": 567,
        "comments": 134,
        "shares": 289,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Waterfall photography during monsoon season 💧🌿 Raw nature beauty!",
        "author": "adventure_seeker",
        "likes": 445,
        "comments": 92,
        "shares": 123,
        "media_type": "video",
        "media_url": "https://example.com/waterfall.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "Sustainable fashion: How to build a capsule wardrobe with ethical brands 👕🌍",
        "author": "eco_warrior",
        "likes": 298,
        "comments": 56,
        "shares": 89,
        "media_type": "image",
        "media_url": "https://example.com/sustainable.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "JavaScript async/await tutorial: Master asynchronous programming with promises and callbacks",
        "author": "code_master",
        "likes": 634,
        "comments": 145,
        "shares": 267,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Garden transformation: From concrete to green paradise in 6 months 🌿🌼",
        "author": "gardening_enthusiast",
        "likes": 378,
        "comments": 71,
        "shares": 102,
        "media_type": "image",
        "media_url": "https://example.com/garden.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Cloud computing architecture: AWS, Google Cloud, Azure comparison and best practices",
        "author": "devops_engineer",
        "likes": 489,
        "comments": 98,
        "shares": 176,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Homemade pizza night 🍕 - Wood-fired oven, fresh mozzarella, and basil perfection!",
        "author": "chef_maria",
        "likes": 356,
        "comments": 64,
        "shares": 98,
        "media_type": "image",
        "media_url": "https://example.com/pizza.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Interior design trends 2024: Minimalism, earth tones, and sustainable materials 🏠✨",
        "author": "design_pro",
        "likes": 401,
        "comments": 79,
        "shares": 145,
        "media_type": "image",
        "media_url": "https://example.com/interior.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Cybersecurity essentials: Password management, encryption, and threat prevention for everyone",
        "author": "security_expert",
        "likes": 512,
        "comments": 112,
        "shares": 234,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Running marathon training plan: 16-week program for beginners 🏃‍♂️💪",
        "author": "fitness_coach",
        "likes": 423,
        "comments": 85,
        "shares": 156,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Desert photography adventure: Golden dunes, starry nights, and endless horizons ✨🏜️",
        "author": "bob_photos",
        "likes": 489,
        "comments": 102,
        "shares": 167,
        "media_type": "image",
        "media_url": "https://example.com/desert.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Database optimization: Indexing, query optimization, and performance tuning strategies",
        "author": "devops_engineer",
        "likes": 578,
        "comments": 123,
        "shares": 289,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Meal prep Sunday: Preparing 5 healthy meals for the week ahead 🥗🥘",
        "author": "healthy_eating",
        "likes": 334,
        "comments": 62,
        "shares": 98,
        "media_type": "image",
        "media_url": "https://example.com/meal-prep.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "Microservices architecture: Breaking monoliths into scalable, maintainable services",
        "author": "code_master",
        "likes": 601,
        "comments": 134,
        "shares": 312,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Ocean conservation: Why protecting marine ecosystems matters for our future 🌊🐠",
        "author": "eco_warrior",
        "likes": 378,
        "comments": 78,
        "shares": 156,
        "media_type": "video",
        "media_url": "https://example.com/ocean.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "Portrait photography: Lighting, poses, and capturing genuine emotions in photos 📸💫",
        "author": "bob_photos",
        "likes": 445,
        "comments": 89,
        "shares": 134,
        "media_type": "image",
        "media_url": "https://example.com/portrait.jpg"
    },
    {
        "id": str(uuid4()),
        "content": "DevOps best practices: CI/CD pipelines, infrastructure as code, monitoring and logging",
        "author": "devops_engineer",
        "likes": 523,
        "comments": 112,
        "shares": 245,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Street food tour: Exploring authentic flavors in Bangkok's night markets 🍜🌶️",
        "author": "travel_vlogger",
        "likes": 512,
        "comments": 98,
        "shares": 178,
        "media_type": "video",
        "media_url": "https://example.com/street-food.mp4"
    },
    {
        "id": str(uuid4()),
        "content": "Creative writing prompts: 30 ideas to spark your imagination and overcome writer's block ✍️",
        "author": "writer_artist",
        "likes": 267,
        "comments": 54,
        "shares": 89,
        "media_type": None,
        "media_url": None
    },
    {
        "id": str(uuid4()),
        "content": "Fruit salad masterpiece - tropical fruits, honey drizzle, and mint garnish 🍉🍓🥝",
        "author": "healthy_eating",
        "likes": 289,
        "comments": 56,
        "shares": 78,
        "media_type": "image",
        "media_url": "https://example.com/fruit-salad.jpg"
    }
]

def seed_database():
    """Add sample posts to the recommender"""
    print(f"Seeding database with {len(sample_posts)} sample posts...")
    
    try:
        # Add all posts to the recommender
        recommender.add_items(sample_posts)
        print(f"✓ Successfully added {len(sample_posts)} posts to FAISS index")
        
        # Clear cache to ensure fresh data
        cache.clear_pattern("*")
        print("✓ Cleared cache")
        
        # Print some stats
        stats = recommender.get_stats()
        print(f"\n📊 Database Stats:")
        print(f"  - Total posts indexed: {stats.get('total_items', 0)}")
        print(f"  - Index dimension: {stats.get('dimension', 384)}")
        print(f"  - Sample posts by category:")
        
        authors = {}
        for post in sample_posts:
            author = post.get("author", "unknown")
            authors[author] = authors.get(author, 0) + 1
        
        for author, count in sorted(authors.items()):
            print(f"    • {author}: {count} posts")
        
        print("\n✅ Database seeding complete!")
        print("\nYou can now:")
        print("  1. View posts in the feed (GET /feed/{user_id})")
        print("  2. Get recommendations (POST /recommend)")
        print("  3. Create new posts (POST /posts/upload)")
        print("  4. Like posts (POST /posts/react)")
        print("  5. Comment on posts (POST /posts/comment)")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    seed_database()
