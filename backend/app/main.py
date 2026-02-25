"""
Social Media Recommender API using FAISS and Sentence Transformers
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import API_TITLE, API_VERSION, DEBUG
from app.recommender import get_recommender
from app.redis_cache import get_cache
from app.embeddings import get_embedder, get_image_embedder
from app.user_behavior import get_analyzer
from app.recommendation_quality import get_quality_monitor, get_pattern_analyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media uploads
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=uploads_dir), name="media")

# Pydantic models
class PostItem(BaseModel):
    id: str
    content: str
    author: Optional[str] = None
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = None


class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 10


class RecommendationResponse(BaseModel):
    query: str
    recommendations: List[Dict[str, Any]]
    cached: bool = False


class InteractionRequest(BaseModel):
    """Track user interaction with a post"""
    user_id: str
    post_id: str
    interaction_type: str  # view, like, comment, share
    watch_time: Optional[int] = 0  # seconds
    metadata: Optional[Dict[str, Any]] = None


class PersonalizedRecommendationRequest(BaseModel):
    """Get personalized recommendations based on user behavior"""
    user_id: str
    top_k: int = 10


# Initialize components
recommender = get_recommender()
cache = get_cache()
embedder = get_embedder()
analyzer = get_analyzer()
quality_monitor = get_quality_monitor()
pattern_analyzer = get_pattern_analyzer()
image_embedder = get_image_embedder()

# In-memory storage for interactions and user profiles
interactions_db: List[Dict] = []
user_profiles: Dict[str, Dict] = {}


# Helper function for async embedding generation
def _generate_post_embeddings(post_id: str, caption: str, image_path: str = None, media_type: str = None):
    """
    Generate text and image embeddings for a post (background task)
    
    Args:
        post_id: Post ID
        caption: Post caption/content
        image_path: Path to image file (if exists)
        media_type: Type of media (image, video, etc)
    """
    try:
        import numpy as np
        
        # Generate text embedding
        if caption:
            text_embedding = embedder.encode_single(caption)
            logger.info(f"Generated text embedding for post {post_id} (dim={len(text_embedding)})")
        else:
            text_embedding = None
        
        # Generate image embedding
        image_embedding = None
        if image_path and media_type == "image" and image_embedder:
            try:
                image_embedding = image_embedder.encode_image_from_file(image_path)
                logger.info(f"Generated image embedding for post {post_id} (dim={len(image_embedding)})")
            except Exception as e:
                logger.warning(f"Failed to generate image embedding for {post_id}: {e}")
        
        # Store embeddings in memory (for now)
        # In production, you'd store these in the database
        if not hasattr(recommender, '_post_embeddings'):
            recommender._post_embeddings = {}
        
        recommender._post_embeddings[post_id] = {
            "text_embedding": text_embedding,
            "image_embedding": image_embedding,
            "has_image": image_embedding is not None
        }
        
        logger.info(f"Embeddings completed for post {post_id}")
        
    except Exception as e:
        logger.error(f"Error generating embeddings for post {post_id}: {e}")


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Social Media Recommender API",
        "version": API_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    stats = recommender.get_stats()
    return {
        "status": "healthy",
        "recommender": stats,
        "cache": "connected" if cache.client else "disconnected"
    }


@app.post("/posts/add")
async def add_post(post: PostItem):
    """Add a single post to the recommendation index"""
    try:
        item = {
            "id": post.id,
            "content": post.content,
            "author": post.author,
            "likes": post.likes,
            "comments": post.comments,
            "shares": post.shares,
            "metadata": post.post_metadata or {}
        }
        
        recommender.add_items([item])
        cache.clear_pattern("recommend:*")  # Clear cache
        
        return {
            "status": "success",
            "message": f"Post {post.id} added to index"
        }
    except Exception as e:
        logger.error(f"Failed to add post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/batch")
async def add_posts_batch(posts: List[PostItem]):
    """Add multiple posts to the recommendation index"""
    try:
        items = [
            {
                "id": post.id,
                "content": post.content,
                "author": post.author,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "metadata": post.post_metadata or {}
            }
            for post in posts
        ]
        
        recommender.add_items(items)
        cache.clear_pattern("recommend:*")  # Clear cache
        
        return {
            "status": "success",
            "message": f"{len(items)} posts added to index"
        }
    except Exception as e:
        logger.error(f"Failed to add posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend")
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get recommendations based on query
    
    Uses cache to speed up repeated queries
    """
    try:
        # Generate cache key
        cache_key = f"recommend:{request.query}:{request.top_k}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return RecommendationResponse(
                query=request.query,
                recommendations=cached_result,
                cached=True
            )
        
        # Search for recommendations
        results = recommender.search(request.query, k=request.top_k)
        
        # Cache the results
        cache.set(cache_key, results)
        
        return RecommendationResponse(
            query=request.query,
            recommendations=results,
            cached=False
        )
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get recommendation index statistics"""
    try:
        stats = recommender.get_stats()
        return {
            "index_stats": stats,
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": 384
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similar")
async def find_similar_content(request: RecommendationRequest):
    """Find similar posts to a given text query"""
    try:
        cache_key = f"similar:{request.query}:{request.top_k}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return {
                "query": request.query,
                "similar_posts": cached_result,
                "cached": True
            }
        
        similar = recommender.search(request.query, k=request.top_k)
        cache.set(cache_key, similar)
        
        return {
            "query": request.query,
            "similar_posts": similar,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Similar search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed")
async def embed_text(text: str):
    """Get embedding for text (for debugging/testing)"""
    try:
        embedding = embedder.encode_single(text)
        return {
            "text": text,
            "embedding": embedding.tolist(),
            "dimension": len(embedding)
        }
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== NEW: MULTIMODAL SEARCH ENDPOINTS ==============

@app.post("/search/multimodal")
async def multimodal_search(
    query_text: str = None,
    query_image_url: str = None,
    top_k: int = 10,
    text_weight: float = 0.5,
    image_weight: float = 0.5
):
    """
    Search using both text and image embeddings
    
    Args:
        query_text: Text query (optional)
        query_image_url: Image URL to search by (optional, auto-embedded with CLIP)
        top_k: Number of results
        text_weight: Weight for text similarity (0-1)
        image_weight: Weight for image similarity (0-1)
    """
    try:
        if not query_text and not query_image_url:
            raise HTTPException(status_code=400, detail="Provide either query_text or query_image_url")
        
        # Generate image embedding if image provided
        query_image_embedding = None
        if query_image_url and image_embedder:
            try:
                query_image_embedding = image_embedder.encode_image_from_url(query_image_url)
                logger.info(f"Generated image embedding from URL")
            except Exception as e:
                logger.warning(f"Failed to embed image from URL: {e}")
        
        # Perform multimodal search
        results = recommender.search_multimodal(
            query_text=query_text,
            query_image_embedding=query_image_embedding,
            k=top_k,
            text_weight=text_weight,
            image_weight=image_weight
        )
        
        return {
            "query_text": query_text,
            "query_image_url": query_image_url,
            "text_weight": text_weight,
            "image_weight": image_weight,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Multimodal search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/by-image")
async def search_by_image(image_url: str, top_k: int = 10):
    """
    Search for visually similar posts using image
    
    Args:
        image_url: URL to query image
        top_k: Number of results
    """
    try:
        if not image_embedder:
            raise HTTPException(status_code=501, detail="Image embeddings not enabled")
        
        # Generate image embedding
        query_image_embedding = image_embedder.encode_image_from_url(image_url)
        
        # Search with image only (no text)
        results = recommender.search_multimodal(
            query_text=None,
            query_image_embedding=query_image_embedding,
            k=top_k,
            text_weight=0.0,
            image_weight=1.0
        )
        
        return {
            "query_image_url": image_url,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed-image")
async def embed_image(image_url: str = None):
    """
    Get CLIP image embedding (512-dim)
    
    Args:
        image_url: URL to image
    """
    try:
        if not image_embedder:
            raise HTTPException(status_code=501, detail="Image embeddings not enabled")
        
        if not image_url:
            raise HTTPException(status_code=400, detail="Provide image_url")
        
        embedding = image_embedder.encode_image_from_url(image_url)
        return {
            "image_url": image_url,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "model": "ViT-B/32 (CLIP)"
        }
    except Exception as e:
        logger.error(f"Image embedding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== BEHAVIOR TRACKING ENDPOINTS ==============

@app.post("/track/interaction")
async def track_interaction(request: InteractionRequest):
    """Track user interaction with a post (view, like, comment, share)"""
    try:
        interaction = analyzer.track_interaction(
            user_id=request.user_id,
            post_id=request.post_id,
            interaction_type=request.interaction_type,
            watch_time=request.watch_time,
            metadata=request.metadata
        )
        
        # Store interaction in database
        interactions_db.append(interaction)
        
        # Update user profile
        if request.user_id not in user_profiles:
            user_profiles[request.user_id] = {
                "user_id": request.user_id,
                "created_at": datetime.utcnow(),
                "total_interactions": 0,
                "preferences": {}
            }
        
        user_profiles[request.user_id]["total_interactions"] += 1
        
        # Clear cache for this user's recommendations
        cache.clear_pattern(f"personalized:{request.user_id}:*")
        
        return {
            "status": "tracked",
            "interaction_id": f"{request.user_id}_{request.post_id}_{request.interaction_type}",
            "message": f"Tracked {request.interaction_type} on post {request.post_id}"
        }
    except Exception as e:
        logger.error(f"Failed to track interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/personalized")
async def get_personalized_recommendations(request: PersonalizedRecommendationRequest):
    """
    Get personalized recommendations based on user behavior
    Auto-recommends posts based on user's viewing, liking, and engagement patterns
    """
    try:
        # Check cache first
        cache_key = f"personalized:{request.user_id}:{request.top_k}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return {
                "user_id": request.user_id,
                "recommendations": cached_result,
                "cached": True,
                "total": len(cached_result)
            }
        
        # Get all posts
        all_posts = recommender.metadata if hasattr(recommender, 'metadata') else []
        
        if not all_posts:
            all_posts = []
        
        # Get recommendations based on user behavior
        recommendations = analyzer.get_recommendations_for_user(
            user_id=request.user_id,
            posts=all_posts,
            interactions=interactions_db,
            top_k=request.top_k
        )
        
        # Cache results
        cache.set(cache_key, recommendations)
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
            "cached": False,
            "total": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Failed to get personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user's inferred preferences based on behavior"""
    try:
        preferences = analyzer.get_user_preferences(user_id, interactions_db)
        
        user_profile = user_profiles.get(user_id, {})
        
        return {
            "user_id": user_id,
            "profile": user_profile,
            "preferences": preferences,
            "total_interactions": len([i for i in interactions_db if i.get("user_id") == user_id])
        }
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/predictions")
async def predict_user_behavior(user_id: str):
    """Predict user's next interests and engagement patterns"""
    try:
        predictions = analyzer.predict_next_interests(user_id, interactions_db)
        
        return {
            "user_id": user_id,
            "predictions": predictions
        }
    except Exception as e:
        logger.error(f"Failed to predict behavior: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    """Get detailed analytics about user's behavior"""
    try:
        user_interactions = [i for i in interactions_db if i.get("user_id") == user_id]
        
        if not user_interactions:
            return {
                "user_id": user_id,
                "analytics": {
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "average_watch_time": 0,
                    "most_active_hour": None,
                    "engagement_rate": 0
                }
            }
        
        # Calculate analytics
        interaction_types = {}
        total_watch_time = 0
        
        for interaction in user_interactions:
            itype = interaction.get("interaction_type", "view")
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
            total_watch_time += interaction.get("watch_time", 0)
        
        total_interactions = len(user_interactions)
        total_engagements = sum(interaction_types.get(t, 0) 
                              for t in ["like", "comment", "share"])
        
        return {
            "user_id": user_id,
            "analytics": {
                "total_views": interaction_types.get("view", 0),
                "total_likes": interaction_types.get("like", 0),
                "total_comments": interaction_types.get("comment", 0),
                "total_shares": interaction_types.get("share", 0),
                "average_watch_time": float(total_watch_time / max(interaction_types.get("view", 1), 1)),
                "engagement_rate": float(total_engagements / max(total_interactions, 1)),
                "total_interactions": total_interactions
            }
        }
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feed/{user_id}")
async def get_social_feed(user_id: str, limit: int = 20):
    """
    Get social media feed with auto-recommended posts
    Similar to Instagram/TikTok feed
    """
    try:
        # Get personalized recommendations
        cache_key = f"feed:{user_id}:{limit}"
        cached_feed = cache.get(cache_key)
        
        if cached_feed:
            return {
                "user_id": user_id,
                "feed": cached_feed,
                "cached": True
            }
        
        # Get all posts
        all_posts = list(recommender.metadata.values()) if hasattr(recommender, 'metadata') and recommender.metadata else []
        if not all_posts:
            all_posts = []
        
        # Get recommendations
        recommendations = analyzer.get_recommendations_for_user(
            user_id=user_id,
            posts=all_posts,
            interactions=interactions_db,
            top_k=limit
        )
        
        # Cache feed
        cache.set(cache_key, recommendations)
        
        return {
            "user_id": user_id,
            "feed": recommendations,
            "cached": False,
            "total": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Failed to get social feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Media and comment storage
media_storage = {}  # post_id -> media_url
comments_storage = {}  # post_id -> list of comments
reactions_storage = {}  # post_id -> {user_id -> reaction}


@app.post("/posts/upload")
async def upload_post(file: UploadFile = File(None), caption: str = Form(""), user_id: str = Form(""), author: str = Form("User"), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Upload a new post with media (image/video)
    Generates text + image embeddings asynchronously
    """
    try:
        from uuid import uuid4
        import shutil
        import os
        from datetime import datetime
        import numpy as np
        
        post_id = str(uuid4())
        
        if file:
            # Save file to storage directory
            uploads_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            
            file_ext = file.filename.split('.')[-1]
            file_path = os.path.join(uploads_dir, f"{post_id}.{file_ext}")
            media_type = "video" if file.content_type.startswith("video") else "image"
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            media_url = f"/media/{post_id}.{file_ext}"
            media_storage[post_id] = media_url
        else:
            media_url = None
            media_type = None
            file_path = None
        
        # Create post item
        item = {
            "id": post_id,
            "content": caption,
            "author": author or "Anonymous",
            "author_id": user_id,
            "author_name": author,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "media_url": media_url,
            "media_type": media_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Generate embeddings asynchronously (background task)
        background_tasks.add_task(
            _generate_post_embeddings,
            post_id,
            caption,
            file_path,
            media_type
        )
        
        # Add to recommender
        recommender.add_items([item])
        
        # Add to interactions tracking
        track_item = {
            "user_id": user_id,
            "post_id": post_id,
            "interaction_type": "create",
            "created_at": datetime.utcnow().isoformat()
        }
        interactions_db.append(track_item)
        
        # Clear cache
        cache.clear_pattern("feed:*")
        
        return {
            "status": "success",
            "post_id": post_id,
            "media_url": media_url,
            "message": "Post created successfully. Processing embeddings..."
        }
    except Exception as e:
        logger.error(f"Failed to upload post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/comment")
async def post_comment(user_id: str, post_id: str, text: str):
    """
    Add a comment to a post
    """
    try:
        from datetime import datetime
        
        if post_id not in comments_storage:
            comments_storage[post_id] = []
        
        comment = {
            "user_id": user_id,
            "author": f"user_{user_id[-4:]}",
            "text": text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        comments_storage[post_id].append(comment)
        
        # Track interaction
        interaction = {
            "user_id": user_id,
            "post_id": post_id,
            "interaction_type": "comment",
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {"comment": text}
        }
        interactions_db.append(interaction)
        
        # Clear cache
        cache.clear_pattern(f"comments:{post_id}")
        cache.clear_pattern("feed:*")
        
        return {
            "status": "success",
            "comment_id": len(comments_storage[post_id]),
            "message": "Comment added successfully"
        }
    except Exception as e:
        logger.error(f"Failed to post comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: str):
    """
    Get all comments for a post
    """
    try:
        comments = comments_storage.get(post_id, [])
        return {
            "post_id": post_id,
            "comments": comments,
            "total": len(comments)
        }
    except Exception as e:
        logger.error(f"Failed to get comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/react")
async def react_to_post(user_id: str, post_id: str, reaction: Optional[str] = None):
    """
    Add or remove a reaction to a post
    reaction can be: ❤️, 😂, 😮, 😢, 😡, etc.
    """
    try:
        if post_id not in reactions_storage:
            reactions_storage[post_id] = {}
        
        if reaction:
            reactions_storage[post_id][user_id] = reaction
            interaction_type = "react"
        else:
            # Remove reaction
            reactions_storage[post_id].pop(user_id, None)
            interaction_type = "unreact"
        
        # Track interaction
        interaction = {
            "user_id": user_id,
            "post_id": post_id,
            "interaction_type": interaction_type,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {"reaction": reaction}
        }
        interactions_db.append(interaction)
        
        # Clear cache
        cache.clear_pattern(f"reactions:{post_id}")
        cache.clear_pattern("feed:*")
        
        return {
            "status": "success",
            "post_id": post_id,
            "reaction": reaction,
            "total_reactions": len(reactions_storage[post_id])
        }
    except Exception as e:
        logger.error(f"Failed to react: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/reactions")
async def get_reactions(post_id: str, user_id: Optional[str] = None):
    """
    Get all reactions for a post
    """
    try:
        reactions = reactions_storage.get(post_id, {})
        user_reaction = reactions.get(user_id) if user_id else None
        
        return {
            "post_id": post_id,
            "user_reaction": user_reaction,
            "reactions": reactions,
            "total": len(reactions),
            "breakdown": {}
        }
    except Exception as e:
        logger.error(f"Failed to get reactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USER POSTS ENDPOINTS ====================

@app.get("/user/{user_id}/posts")
async def get_user_posts(user_id: str):
    """
    Get all posts created by a specific user
    """
    try:
        # Get all items from recommender
        stats = recommender.get_stats()
        metadata = recommender.get_metadata()
        
        user_posts = []
        if metadata:
            for idx, meta in enumerate(metadata):
                if meta.get('author_id') == user_id or meta.get('user_id') == user_id:
                    user_posts.append(meta)
        
        return {
            "user_id": user_id,
            "posts": user_posts,
            "total": len(user_posts)
        }
    except Exception as e:
        logger.error(f"Failed to get user posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, request: dict):
    """
    Delete a post (if user is the author)
    """
    try:
        user_id = request.get("user_id")
        
        # Remove from recommender
        metadata = recommender.get_metadata()
        for idx, meta in enumerate(metadata):
            if meta.get('id') == post_id and (meta.get('author_id') == user_id or meta.get('user_id') == user_id):
                recommender.remove_item(idx)
                return {"status": "deleted", "post_id": post_id}
        
        raise HTTPException(status_code=403, detail="Unauthorized to delete this post")
    except Exception as e:
        logger.error(f"Failed to delete post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/posts")
async def search_posts(query: str, limit: int = 50):
    """
    Search for posts by content, author, or hashtags
    """
    try:
        # Use recommender for semantic search
        results = recommender.search(query, top_k=limit)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Failed to search posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trending")
async def get_trending_posts(limit: int = 20):
    """
    Get trending posts (sorted by engagement)
    """
    try:
        stats = recommender.get_stats()
        metadata = recommender.metadata if hasattr(recommender, 'metadata') else {}
        
        # Convert metadata to list if needed
        if isinstance(metadata, dict):
            posts = list(metadata.values())
        else:
            posts = metadata
        
        # Sort by likes + comments
        trending = sorted(
            posts,
            key=lambda x: (x.get('likes', 0) + x.get('comments', 0)),
            reverse=True
        )[:limit]
        
        return {
            "posts": trending,
            "count": len(trending)
        }
    except Exception as e:
        logger.error(f"Failed to get trending posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== ENHANCED DIAGNOSTICS & OPTIMIZATION ==============

@app.get("/diagnostics/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        stats = recommender.get_stats()
        metrics = recommender.metrics.get_stats() if hasattr(recommender, 'metrics') else {}
        
        return {
            "recommender": stats,
            "performance": metrics,
            "users_tracked": len(user_profiles),
            "total_interactions": len(interactions_db),
            "cache_stats": cache.get_stats() if hasattr(cache, 'get_stats') else {}
        }
    except Exception as e:
        logger.error(f"Failed to get diagnostics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize/reindex")
async def reindex_recommender():
    """Rebuild FAISS index for optimization (intensive operation)"""
    try:
        logger.info("Starting reindex operation...")
        recommender.reindex()
        
        return {
            "status": "success",
            "message": "Index rebuilt and optimized",
            "new_stats": recommender.get_stats()
        }
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize/clear-caches")
async def clear_caches():
    """Clear all internal caches to free memory"""
    try:
        recommender.clear_caches()
        cache.flush_all()
        
        return {
            "status": "success",
            "message": "All caches cleared"
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/insights")
async def get_user_insights(user_id: str):
    """Get comprehensive insights about user's behavior"""
    try:
        insights = analyzer.get_user_insights(user_id, interactions_db)
        
        return {
            "user_id": user_id,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/advanced")
async def advanced_recommendation(
    user_id: str,
    top_k: int = 10,
    diversity_boost: float = 0.0,
    freshness_weight: float = 0.0
):
    """
    Advanced recommendation endpoint with customizable parameters
    
    Args:
        user_id: User ID for personalization
        top_k: Number of recommendations
        diversity_boost: Boost result diversity (0-1)
        freshness_weight: Weight for fresh content (0-1)
    """
    try:
        cache_key = f"advanced_rec:{user_id}:{top_k}:{diversity_boost}:{freshness_weight}"
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            return {
                "user_id": user_id,
                "recommendations": cached,
                "cached": True
            }
        
        # Get user's interaction history
        user_interactions = [i for i in interactions_db if i.get("user_id") == user_id]
        
        # Get all posts as list
        metadata = recommender.metadata if hasattr(recommender, 'metadata') else {}
        if isinstance(metadata, dict):
            posts = list(metadata.values())
        else:
            posts = metadata
        
        # Get personalized recommendations
        recommendations = analyzer.get_recommendations_for_user(
            user_id=user_id,
            posts=posts,
            interactions=interactions_db,
            top_k=top_k
        )
        
        # Apply advanced filters
        if diversity_boost > 0:
            recommendations = self._apply_diversity_filter(recommendations, diversity_boost)
        
        if freshness_weight > 0:
            recommendations.sort(
                key=lambda x: x.get('freshness_score', 0),
                reverse=True
            )
        
        recommendations = recommendations[:top_k]
        
        # Cache results
        cache.set(cache_key, recommendations)
        
        return {
            "user_id": user_id,
            "parameters": {
                "top_k": top_k,
                "diversity_boost": diversity_boost,
                "freshness_weight": freshness_weight
            },
            "recommendations": recommendations,
            "cached": False,
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Advanced recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _apply_diversity_filter(recommendations: List[Dict], diversity_boost: float) -> List[Dict]:
    """Apply diversity filtering to recommendations"""
    if not recommendations or diversity_boost <= 0:
        return recommendations
    
    filtered = [recommendations[0]]
    
    for rec in recommendations[1:]:
        # Check diversity with already selected items
        is_diverse = True
        for selected in filtered:
            if rec.get('author') == selected.get('author'):
                if diversity_boost > 0.5:  # High diversity: exclude same author
                    is_diverse = False
                    break
        
        if is_diverse:
            filtered.append(rec)
    
    return filtered


# ============== QUALITY MONITORING & ANOMALY DETECTION ==============

@app.post("/quality/assess")
async def assess_recommendation_quality(
    user_id: str,
    top_k: int = 10
):
    """Assess quality of recommendations for a user"""
    try:
        # Get user interactions
        user_interactions = [i for i in interactions_db if i.get("user_id") == user_id]
        
        # Get personalized recommendations
        metadata = recommender.metadata if hasattr(recommender, 'metadata') else {}
        if isinstance(metadata, dict):
            posts = list(metadata.values())
        else:
            posts = metadata
        
        recommendations = analyzer.get_recommendations_for_user(
            user_id=user_id,
            posts=posts,
            interactions=interactions_db,
            top_k=top_k
        )
        
        # Get user preferences
        user_prefs = analyzer.get_user_preferences(user_id, interactions_db)
        
        # Generate quality report
        quality_report = quality_monitor.get_quality_report(
            recommendations,
            user_interactions,
            user_prefs
        )
        
        return {
            "user_id": user_id,
            "quality_report": quality_report
        }
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quality/feedback")
async def record_recommendation_feedback(
    user_id: str,
    post_id: str,
    interaction_type: str,
    relevance_rating: Optional[float] = None
):
    """Record user feedback on recommendation quality"""
    try:
        feedback = quality_monitor.record_recommendation_feedback(
            user_id=user_id,
            recommended_post_id=post_id,
            interaction_type=interaction_type,
            relevance_rating=relevance_rating
        )
        
        return {
            "status": "success",
            "feedback_recorded": feedback
        }
    except Exception as e:
        logger.error(f"Feedback recording failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomalies/detect")
async def detect_user_anomalies(user_id: str):
    """Detect anomalies in user interaction patterns"""
    try:
        # Get user interactions
        user_interactions = [i for i in interactions_db if i.get("user_id") == user_id]
        
        # Get recommendations for this user
        metadata = recommender.metadata if hasattr(recommender, 'metadata') else {}
        if isinstance(metadata, dict):
            posts = list(metadata.values())
        else:
            posts = metadata
        
        recommendations = analyzer.get_recommendations_for_user(
            user_id=user_id,
            posts=posts,
            interactions=interactions_db,
            top_k=10
        )
        
        # Detect anomalies
        anomalies = quality_monitor.detect_anomalies(recommendations, user_interactions)
        
        # Detect bot behavior
        is_bot, bot_confidence = pattern_analyzer.detect_bot_behavior(user_interactions)
        
        # Get session info
        session_info = pattern_analyzer.get_user_session_info(user_interactions)
        
        return {
            "user_id": user_id,
            "anomalies": anomalies,
            "bot_detection": {
                "is_suspicious": is_bot,
                "confidence": round(bot_confidence, 3)
            },
            "session_info": session_info
        }
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/system")
async def get_system_analytics():
    """Get comprehensive system analytics"""
    try:
        # Get recommender stats
        rec_stats = recommender.get_stats()
        perf_metrics = recommender.metrics.get_stats()
        
        # Calculate interaction statistics
        interaction_counts = {}
        for i in interactions_db:
            itype = i.get("interaction_type", "unknown")
            interaction_counts[itype] = interaction_counts.get(itype, 0) + 1
        
        # Calculate user statistics
        unique_users = len(set(i.get("user_id") for i in interactions_db))
        unique_posts = len(set(i.get("post_id") for i in interactions_db))
        
        # Calculate engagement metrics
        avg_interactions_per_user = len(interactions_db) / max(unique_users, 1)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "recommender": rec_stats,
            "performance": perf_metrics,
            "interactions": {
                "total": len(interactions_db),
                "by_type": interaction_counts,
                "avg_per_user": round(avg_interactions_per_user, 2)
            },
            "users": {
                "total": unique_users,
                "with_interactions": unique_users
            },
            "posts": {
                "total": unique_posts,
                "with_interactions": unique_posts
            }
        }
    except Exception as e:
        logger.error(f"System analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/user/{user_id}")
async def get_user_analytics(user_id: str):
    """Get detailed analytics for a specific user"""
    try:
        # Get user interactions
        user_interactions = [i for i in interactions_db if i.get("user_id") == user_id]
        
        if not user_interactions:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user preferences and insights
        preferences = analyzer.get_user_preferences(user_id, interactions_db)
        insights = analyzer.get_user_insights(user_id, interactions_db)
        
        # Get session info
        session_info = pattern_analyzer.get_user_session_info(user_interactions)
        
        # Calculate engagement metrics
        interaction_types = {}
        for i in user_interactions:
            itype = i.get("interaction_type", "unknown")
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        return {
            "user_id": user_id,
            "profile": user_profiles.get(user_id, {}),
            "preferences": preferences,
            "insights": insights,
            "engagement": {
                "total_interactions": len(user_interactions),
                "by_type": interaction_types,
                "session_info": session_info
            },
            "activity_timeline": [
                {
                    "interaction_type": i.get("interaction_type"),
                    "post_id": i.get("post_id"),
                    "timestamp": i.get("timestamp", "").isoformat() if hasattr(i.get("timestamp"), "isoformat") else str(i.get("timestamp"))
                }
                for i in user_interactions[-20:]  # Last 20 interactions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


