"""
Enhanced user behavior tracking and analysis module
Implements collaborative filtering, content-based filtering, and hybrid approaches
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict, Counter
from scipy.spatial.distance import cosine
from .db import InteractionLog, User, Post

class UserBehaviorAnalyzer:
    """Advanced user behavior analysis with multiple recommendation strategies"""
    
    def __init__(self):
        self.behavior_window = 30  # Days to analyze
        self.min_interactions = 3  # Minimum interactions for recommendations
        self.interaction_decay = 0.95  # Decay factor for old interactions (per day)
        
        # Interaction weights (higher = more important)
        self.interaction_weights = {
            "view": 1.0,
            "like": 5.0,
            "comment": 10.0,
            "share": 20.0,
            "bookmark": 15.0
        }
        
        # Weighting for recommendation components
        self.weights = {
            "content_similarity": 0.4,
            "user_preference": 0.3,
            "engagement_level": 0.2,
            "freshness": 0.1
        }
    
    def track_interaction(self, user_id: str, post_id: str, interaction_type: str, 
                         watch_time: int = 0, metadata: dict = None) -> Dict:
        """Track user interaction with enhanced metadata"""
        return {
            "user_id": user_id,
            "post_id": post_id,
            "interaction_type": interaction_type,  # view, like, comment, share, bookmark
            "watch_time": watch_time,  # seconds
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
            "weight": self.interaction_weights.get(interaction_type, 1.0)
        }
    
    def get_user_preferences(self, user_id: str, interactions: List[Dict]) -> Dict:
        """Extract comprehensive user preferences from interaction history"""
        
        if not interactions:
            return self._empty_preferences()
        
        # Get user interactions
        user_interactions = [i for i in interactions if i.get("user_id") == user_id]
        
        if not user_interactions:
            return self._empty_preferences()
        
        # Calculate interaction metrics with time decay
        weighted_interactions = self._apply_time_decay(user_interactions)
        interaction_types = Counter(i.get("interaction_type") for i in user_interactions)
        
        # Calculate watch time statistics
        watch_times = [i.get("watch_time", 0) for i in user_interactions]
        avg_watch_time = np.mean(watch_times) if watch_times else 0
        
        # Calculate engagement score (weighted)
        engagement_score = sum(
            interaction_types.get(itype, 0) * self.interaction_weights.get(itype, 1.0)
            for itype in interaction_types
        )
        
        # Extract author and topic preferences
        preferred_authors = Counter(
            i.get("metadata", {}).get("author") 
            for i in weighted_interactions 
            if i.get("metadata", {}).get("author")
        ).most_common(5)
        
        preferred_topics = Counter(
            i.get("metadata", {}).get("topic") 
            for i in weighted_interactions 
            if i.get("metadata", {}).get("topic")
        ).most_common(5)
        
        # Calculate interaction patterns
        interaction_recency = self._calculate_recency_score(user_interactions)
        interaction_frequency = self._calculate_frequency_score(user_interactions)
        
        return {
            "preferred_authors": [author for author, _ in preferred_authors],
            "preferred_topics": [topic for topic, _ in preferred_topics],
            "interaction_frequency": dict(interaction_types),
            "average_watch_time": float(avg_watch_time),
            "engagement_score": float(engagement_score),
            "total_interactions": len(user_interactions),
            "recency_score": interaction_recency,
            "frequency_score": interaction_frequency,
            "interaction_velocity": self._calculate_interaction_velocity(user_interactions),
            "content_length_preference": self._estimate_length_preference(user_interactions)
        }
    
    def _empty_preferences(self) -> Dict:
        """Return empty/default preferences"""
        return {
            "preferred_authors": [],
            "preferred_topics": [],
            "interaction_frequency": {},
            "average_watch_time": 0,
            "engagement_score": 0,
            "total_interactions": 0,
            "recency_score": 0.5,
            "frequency_score": 0.5,
            "interaction_velocity": 0,
            "content_length_preference": "medium"
        }
    
    def _apply_time_decay(self, interactions: List[Dict]) -> List[Dict]:
        """Apply exponential decay to older interactions"""
        decayed = []
        now = datetime.utcnow()
        
        for interaction in interactions:
            timestamp = interaction.get("timestamp", now)
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            days_old = (now - timestamp).days
            decay_factor = self.interaction_decay ** days_old
            
            decayed_interaction = interaction.copy()
            decayed_interaction['weight'] = interaction.get('weight', 1.0) * decay_factor
            decayed.append(decayed_interaction)
        
        return decayed
    
    def _calculate_recency_score(self, interactions: List[Dict]) -> float:
        """Calculate how recent user's interactions are (0-1)"""
        if not interactions:
            return 0.5
        
        timestamps = [i.get("timestamp") for i in interactions if i.get("timestamp")]
        if not timestamps:
            return 0.5
        
        # Convert string timestamps if needed
        timestamps = [
            datetime.fromisoformat(ts) if isinstance(ts, str) else ts 
            for ts in timestamps
        ]
        
        most_recent = max(timestamps)
        days_since_last = (datetime.utcnow() - most_recent).days
        
        # Score: 1.0 if today, decays over 30 days
        return max(0.0, 1.0 - (days_since_last / 30.0))
    
    def _calculate_frequency_score(self, interactions: List[Dict]) -> float:
        """Calculate interaction frequency (0-1)"""
        if not interactions:
            return 0.0
        
        # Interactions per day
        if len(interactions) < 2:
            return 0.5
        
        timestamps = sorted([
            datetime.fromisoformat(i.get("timestamp")) 
            if isinstance(i.get("timestamp"), str) 
            else i.get("timestamp")
            for i in interactions 
            if i.get("timestamp")
        ])
        
        if len(timestamps) < 2:
            return 0.5
        
        total_days = (timestamps[-1] - timestamps[0]).days + 1
        frequency = len(interactions) / max(total_days, 1)
        
        # Normalize: 1 interaction/day = score 1.0
        return min(1.0, frequency)
    
    def _calculate_interaction_velocity(self, interactions: List[Dict]) -> float:
        """Calculate rate of interaction increase"""
        if len(interactions) < 5:
            return 0.0
        
        # Compare recent vs older interactions
        mid_point = len(interactions) // 2
        recent_density = len(interactions) - mid_point
        older_density = mid_point
        
        if older_density == 0:
            return 1.0
        
        return min(1.0, (recent_density - older_density) / older_density)
    
    def _estimate_length_preference(self, interactions: List[Dict]) -> str:
        """Estimate preferred content length based on watch times"""
        watch_times = [i.get("watch_time", 0) for i in interactions]
        if not watch_times:
            return "medium"
        
        avg_time = np.mean(watch_times)
        if avg_time < 10:
            return "short"
        elif avg_time < 30:
            return "medium"
        else:
            return "long"
    
    def get_recommendations_for_user(self, user_id: str, 
                                     posts: List[Dict],
                                     interactions: List[Dict],
                                     embeddings_map: Optional[Dict] = None,
                                     top_k: int = 10) -> List[Dict]:
        """
        Generate hybrid personalized recommendations using multiple strategies
        Combines: content-based, collaborative, popularity, and freshness signals
        """
        
        user_prefs = self.get_user_preferences(user_id, interactions)
        
        # Get posts user hasn't interacted with
        interacted_post_ids = {
            i.get("post_id") 
            for i in interactions 
            if i.get("user_id") == user_id
        }
        
        unviewed_posts = [
            p for p in posts 
            if p.get("id") not in interacted_post_ids
        ]
        
        if not unviewed_posts:
            return sorted(posts, key=lambda x: x.get("likes", 0), reverse=True)[:top_k]
        
        # Score each post using multiple factors
        scored_posts = []
        for post in unviewed_posts:
            
            # 1. Content-based score (popularity metrics)
            engagement_score = self._calculate_engagement_score(post)
            
            # 2. User preference match score
            preference_score = self._calculate_preference_match(post, user_prefs)
            
            # 3. Collaborative filtering score (similar to posts user liked)
            collaborative_score = self._calculate_collaborative_score(
                user_id, post, interactions, posts, embeddings_map
            )
            
            # 4. Freshness score (boost recent content)
            freshness_score = self._calculate_freshness(post)
            
            # Weighted combination of all factors
            final_score = (
                engagement_score * self.weights["engagement_level"] +
                preference_score * self.weights["user_preference"] +
                collaborative_score * self.weights["content_similarity"] +
                freshness_score * self.weights["freshness"]
            )
            
            scored_posts.append({
                **post,
                "recommendation_score": float(final_score),
                "engagement_score": float(engagement_score),
                "preference_score": float(preference_score),
                "collaborative_score": float(collaborative_score),
                "freshness_score": float(freshness_score),
                "recommendation_reason": self._get_recommendation_reason(
                    post, user_prefs, {
                        "engagement": engagement_score,
                        "preference": preference_score,
                        "collaborative": collaborative_score,
                        "freshness": freshness_score
                    }
                )
            })
        
        # Sort by recommendation score
        scored_posts.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
        
        return scored_posts[:top_k]
    
    def _calculate_engagement_score(self, post: Dict) -> float:
        """Calculate how engaging/popular a post is (0-1)"""
        likes = post.get("likes", 0)
        comments = post.get("comments", 0)
        shares = post.get("shares", 0)
        
        # Weighted engagement (shares are rarest, so weighted highest)
        raw_score = likes * 0.4 + comments * 0.4 + shares * 0.2
        
        # Normalize using sigmoid (prevents extremes)
        normalized = 1.0 / (1.0 + np.exp(-raw_score / 100))
        return float(normalized)
    
    def _calculate_preference_match(self, post: Dict, user_prefs: Dict) -> float:
        """Calculate how much a post matches user's preferences (0-1)"""
        score = 0.5  # Base score
        
        # Author matching
        if post.get("author") in user_prefs.get("preferred_authors", []):
            score += 0.2
        
        # Topic matching
        if post.get("topic") in user_prefs.get("preferred_topics", []):
            score += 0.2
        
        # Content length matching
        post_length = len(post.get("content", "").split())
        pref_length = user_prefs.get("content_length_preference", "medium")
        
        if pref_length == "short" and post_length < 100:
            score += 0.1
        elif pref_length == "medium" and 100 <= post_length < 300:
            score += 0.1
        elif pref_length == "long" and post_length >= 300:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_collaborative_score(self, user_id: str, post: Dict,
                                      interactions: List[Dict], 
                                      posts: List[Dict],
                                      embeddings_map: Optional[Dict]) -> float:
        """
        Collaborative filtering: find similar users and see what they liked
        """
        user_liked_posts = {
            i.get("post_id")
            for i in interactions
            if i.get("user_id") == user_id and i.get("interaction_type") in ["like", "bookmark"]
        }
        
        if not user_liked_posts:
            return 0.5  # Default score if no likes
        
        # Find other users who liked similar posts
        similar_users = defaultdict(int)
        for interaction in interactions:
            if (interaction.get("post_id") in user_liked_posts and 
                interaction.get("user_id") != user_id and
                interaction.get("interaction_type") in ["like", "bookmark"]):
                similar_users[interaction.get("user_id")] += 1
        
        if not similar_users:
            return 0.5
        
        # Check if similar users liked this post
        score = 0.0
        for similar_user, weight in similar_users.items():
            if any(i.get("user_id") == similar_user and 
                  i.get("post_id") == post.get("id") and
                  i.get("interaction_type") in ["like", "bookmark"]
                  for i in interactions):
                score += weight / len(similar_users)
        
        return float(min(1.0, score))
    
    def _calculate_freshness(self, post: Dict) -> float:
        """Calculate freshness score (0-1, higher = newer)"""
        try:
            created_at = post.get("created_at")
            if not created_at:
                return 0.5
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            days_old = (datetime.utcnow() - created_at).days
            
            # Exponential decay: 7-day half-life
            freshness = np.exp(-days_old / 7.0)
            return float(freshness)
        except Exception:
            return 0.5
    
    def _get_recommendation_reason(self, post: Dict, user_prefs: Dict, scores: Dict = None) -> str:
        """Generate human-readable reason for recommendation"""
        if not scores:
            scores = {}
        
        # Determine dominant scoring factor
        dominant_factor = max(scores.items(), key=lambda x: x[1])[0] if scores else None
        
        if dominant_factor == "freshness":
            return "🔥 New and trending"
        elif dominant_factor == "collaborative":
            return "👥 Liked by similar users"
        elif dominant_factor == "preference":
            return f"⭐ Matches your interests"
        elif dominant_factor == "engagement":
            return "📈 Trending content"
        
        # Fallback reasons
        if post.get("likes", 0) > 500:
            return "🔥 Trending in your interest area"
        
        if post.get("comments", 0) > 20:
            return "💬 Highly discussed topic"
        
        return "✨ Recommended for you"
    
    def predict_next_interests(self, user_id: str, 
                              interactions: List[Dict]) -> Dict:
        """Predict user's next likely interests with confidence scores"""
        
        user_interactions = [
            i for i in interactions 
            if i.get("user_id") == user_id
        ]
        
        if not user_interactions:
            return {
                "predicted_topics": [],
                "next_engagement_time": None,
                "predicted_interaction_type": "view",
                "confidence": 0.0,
                "predicted_content_type": "any",
                "activity_pattern": "inactive"
            }
        
        # Get recent interactions
        recent_interactions = sorted(
            user_interactions,
            key=lambda x: x.get("timestamp", datetime.utcnow()),
            reverse=True
        )[:10]
        
        # Analyze interaction types pattern
        interaction_types = [i.get("interaction_type") for i in recent_interactions]
        type_counter = Counter(interaction_types)
        most_common_type = type_counter.most_common(1)[0][0] if type_counter else "view"
        type_confidence = type_counter[most_common_type] / len(recent_interactions) if recent_interactions else 0
        
        # Estimate next engagement time
        timestamps = [i.get("timestamp") for i in recent_interactions if i.get("timestamp")]
        timestamps = [
            datetime.fromisoformat(ts) if isinstance(ts, str) else ts 
            for ts in timestamps
        ]
        
        next_engagement = None
        engagement_confidence = 0.0
        
        if len(timestamps) > 1:
            time_diffs = [
                (timestamps[i-1] - timestamps[i]).total_seconds() 
                for i in range(1, len(timestamps))
            ]
            avg_time_diff = np.mean(time_diffs) if time_diffs else 0
            std_time_diff = np.std(time_diffs) if time_diffs else 0
            
            next_engagement = datetime.utcnow() + timedelta(seconds=avg_time_diff)
            # Confidence: lower std = higher confidence
            engagement_confidence = max(0.0, 1.0 - (std_time_diff / (avg_time_diff + 1)))
        
        # Predict activity pattern
        if type_confidence > 0.7:
            activity_pattern = "consistent"
        elif type_confidence > 0.5:
            activity_pattern = "varied"
        else:
            activity_pattern = "unpredictable"
        
        return {
            "predicted_topics": [],
            "next_engagement_time": next_engagement.isoformat() if next_engagement else None,
            "predicted_interaction_type": most_common_type,
            "confidence": float(max(type_confidence, engagement_confidence)),
            "predicted_content_type": self._predict_content_type(recent_interactions),
            "activity_pattern": activity_pattern
        }
    
    def _predict_content_type(self, interactions: List[Dict]) -> str:
        """Predict what type of content user will likely engage with next"""
        content_types = Counter()
        
        for interaction in interactions:
            metadata = interaction.get("metadata", {})
            content_type = metadata.get("content_type", "text")
            interaction_type = interaction.get("interaction_type", "view")
            
            # Weight higher for likes/shares than views
            weight = {"view": 1, "like": 2, "comment": 3, "share": 4}.get(interaction_type, 1)
            content_types[content_type] += weight
        
        if not content_types:
            return "any"
        
        return content_types.most_common(1)[0][0]
    
    def get_user_insights(self, user_id: str, interactions: List[Dict]) -> Dict:
        """Generate comprehensive insights about user behavior"""
        user_prefs = self.get_user_preferences(user_id, interactions)
        predictions = self.predict_next_interests(user_id, interactions)
        
        user_interactions = [i for i in interactions if i.get("user_id") == user_id]
        
        if user_interactions:
            # Calculate activity level
            timestamps = sorted([
                datetime.fromisoformat(i.get("timestamp"))
                if isinstance(i.get("timestamp"), str)
                else i.get("timestamp")
                for i in user_interactions
                if i.get("timestamp")
            ])
            
            if len(timestamps) >= 2:
                days_span = (timestamps[-1] - timestamps[0]).days + 1
                daily_avg = len(user_interactions) / max(days_span, 1)
            else:
                daily_avg = len(user_interactions)
        else:
            daily_avg = 0
        
        return {
            "user_id": user_id,
            "total_interactions": user_prefs.get("total_interactions", 0),
            "engagement_score": user_prefs.get("engagement_score", 0),
            "engagement_level": self._categorize_engagement(user_prefs.get("engagement_score", 0)),
            "avg_daily_activity": round(daily_avg, 2),
            "recency_score": user_prefs.get("recency_score", 0),
            "activity_status": "active" if user_prefs.get("recency_score", 0) > 0.5 else "inactive",
            "preferred_interaction": max(user_prefs.get("interaction_frequency", {}).items(), 
                                         key=lambda x: x[1])[0] if user_prefs.get("interaction_frequency") else "view",
            "favorite_authors": user_prefs.get("preferred_authors", [])[:3],
            "favorite_topics": user_prefs.get("preferred_topics", [])[:3],
            "content_length_pref": user_prefs.get("content_length_preference", "medium"),
            "next_predicted_engagement": predictions.get("next_engagement_time"),
            "prediction_confidence": round(predictions.get("confidence", 0), 2)
        }
    
    def _categorize_engagement(self, engagement_score: float) -> str:
        """Categorize user engagement level"""
        if engagement_score >= 100:
            return "very_high"
        elif engagement_score >= 50:
            return "high"
        elif engagement_score >= 20:
            return "moderate"
        elif engagement_score > 0:
            return "low"
        else:
            return "none"


# Global analyzer instance
_analyzer = None

def get_analyzer() -> UserBehaviorAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = UserBehaviorAnalyzer()
    return _analyzer
