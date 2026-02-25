"""
Recommendation Quality Assessment & Anomaly Detection
Monitors recommendation system health and detects issues
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RecommendationQualityMonitor:
    """Monitor and assess recommendation quality metrics"""
    
    def __init__(self):
        self.interaction_history = defaultdict(list)  # user_id -> list of interactions
        self.recommendation_feedback = defaultdict(list)  # rec_id -> list of feedback
        self.performance_metrics = {
            "click_through_rate": 0.0,
            "conversion_rate": 0.0,
            "diversity_score": 0.0,
            "relevance_score": 0.0,
            "novelty_score": 0.0
        }
        self.anomalies_detected = []
        self.quality_threshold = 0.6  # Minimum acceptable quality score
    
    def record_recommendation_feedback(self, 
                                      user_id: str,
                                      recommended_post_id: str,
                                      interaction_type: str,
                                      relevance_rating: Optional[float] = None) -> Dict:
        """Record user feedback on recommendations"""
        
        feedback = {
            "user_id": user_id,
            "post_id": recommended_post_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.utcnow(),
            "relevance_rating": relevance_rating
        }
        
        rec_id = f"{user_id}_{recommended_post_id}"
        self.recommendation_feedback[rec_id].append(feedback)
        
        return feedback
    
    def calculate_ctr(self, recommendations: List[Dict], interactions: List[Dict]) -> float:
        """Calculate Click-Through Rate (CTR) for recommendations"""
        
        if not recommendations:
            return 0.0
        
        # Get post IDs from recommendations
        rec_post_ids = {rec.get("id") for rec in recommendations}
        
        # Count how many were clicked/interacted
        clicked = sum(
            1 for i in interactions 
            if i.get("post_id") in rec_post_ids 
            and i.get("interaction_type") in ["click", "like", "comment", "share"]
        )
        
        return clicked / len(recommendations) if recommendations else 0.0
    
    def calculate_diversity_score(self, recommendations: List[Dict]) -> float:
        """
        Calculate diversity score of recommendations
        Higher diversity = less similar posts recommended
        """
        
        if len(recommendations) <= 1:
            return 1.0
        
        # Check for diversity across multiple dimensions
        authors = set(rec.get("author") for rec in recommendations)
        categories = set(rec.get("category") for rec in recommendations)
        
        # Normalize by expected diversity
        author_diversity = len(authors) / len(recommendations)
        category_diversity = len(categories) / len(recommendations)
        
        # Combined diversity score
        diversity = (author_diversity + category_diversity) / 2
        return min(diversity, 1.0)
    
    def calculate_relevance_score(self, 
                                 recommendations: List[Dict],
                                 user_preferences: Dict) -> float:
        """Calculate relevance of recommendations to user preferences"""
        
        if not recommendations or not user_preferences:
            return 0.0
        
        relevance_scores = []
        
        for rec in recommendations:
            # Calculate relevance based on multiple factors
            author_match = 1.0 if rec.get("author") in user_preferences.get("preferred_authors", []) else 0.5
            category_match = 1.0 if rec.get("category") in user_preferences.get("preferred_topics", []) else 0.5
            
            # Weighted relevance
            rec_relevance = (author_match + category_match) / 2
            relevance_scores.append(rec_relevance)
        
        return np.mean(relevance_scores) if relevance_scores else 0.0
    
    def calculate_novelty_score(self,
                               recommendations: List[Dict],
                               user_history: List[Dict]) -> float:
        """
        Calculate novelty score - how new/fresh the recommendations are
        Higher = more novel content recommended
        """
        
        if not recommendations:
            return 0.0
        
        # Get IDs from user history
        history_ids = {item.get("id") for item in user_history}
        
        # Count novel recommendations
        novel_recs = sum(1 for rec in recommendations if rec.get("id") not in history_ids)
        
        novelty = novel_recs / len(recommendations) if recommendations else 0.0
        return min(novelty, 1.0)
    
    def calculate_overall_quality_score(self,
                                       recommendations: List[Dict],
                                       user_interactions: List[Dict],
                                       user_preferences: Dict) -> float:
        """
        Calculate overall recommendation quality score (0-1)
        Combines multiple metrics
        """
        
        ctr = self.calculate_ctr(recommendations, user_interactions)
        diversity = self.calculate_diversity_score(recommendations)
        relevance = self.calculate_relevance_score(recommendations, user_preferences)
        novelty = self.calculate_novelty_score(recommendations, user_interactions)
        
        # Weighted combination
        overall_score = (
            ctr * 0.3 +
            diversity * 0.2 +
            relevance * 0.35 +
            novelty * 0.15
        )
        
        return min(overall_score, 1.0)
    
    def detect_anomalies(self,
                        recommendations: List[Dict],
                        user_interactions: List[Dict]) -> Dict:
        """Detect anomalies in recommendation patterns"""
        
        anomalies = {
            "detected": [],
            "severity": "none",
            "actions": []
        }
        
        # Check 1: All recommendations from same author
        authors = [rec.get("author") for rec in recommendations]
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        max_author_count = max(author_counts.values()) if author_counts else 0
        if max_author_count / len(recommendations) > 0.7 if recommendations else False:
            anomalies["detected"].append("low_diversity")
            anomalies["severity"] = "medium"
            anomalies["actions"].append("Rebalance recommendations across different authors")
        
        # Check 2: All recommendations too old
        if recommendations:
            ages = []
            for rec in recommendations:
                if "created_at" in rec:
                    try:
                        age = (datetime.utcnow() - datetime.fromisoformat(rec["created_at"])).days
                        ages.append(age)
                    except:
                        pass
            
            if ages and np.mean(ages) > 30:
                anomalies["detected"].append("stale_content")
                anomalies["severity"] = "high"
                anomalies["actions"].append("Prioritize fresher content in recommendations")
        
        # Check 3: User has seen all recommendations before
        rec_ids = {rec.get("id") for rec in recommendations}
        history_ids = {item.get("id") for item in user_interactions}
        
        if rec_ids and rec_ids.issubset(history_ids):
            anomalies["detected"].append("no_novelty")
            anomalies["severity"] = "high"
            anomalies["actions"].append("Include more novel/unseen content")
        
        # Check 4: Empty recommendations
        if not recommendations:
            anomalies["detected"].append("no_recommendations")
            anomalies["severity"] = "high"
            anomalies["actions"].append("Fallback to trending content")
        
        if anomalies["detected"]:
            self.anomalies_detected.append({
                "timestamp": datetime.utcnow(),
                "anomalies": anomalies
            })
        
        return anomalies
    
    def get_quality_report(self,
                          recommendations: List[Dict],
                          user_interactions: List[Dict],
                          user_preferences: Dict) -> Dict:
        """Generate comprehensive quality report"""
        
        quality_score = self.calculate_overall_quality_score(
            recommendations,
            user_interactions,
            user_preferences
        )
        
        anomalies = self.detect_anomalies(recommendations, user_interactions)
        
        report = {
            "quality_score": round(quality_score, 3),
            "quality_status": "good" if quality_score > self.quality_threshold else "poor",
            "metrics": {
                "ctr": round(self.calculate_ctr(recommendations, user_interactions), 3),
                "diversity": round(self.calculate_diversity_score(recommendations), 3),
                "relevance": round(self.calculate_relevance_score(recommendations, user_preferences), 3),
                "novelty": round(self.calculate_novelty_score(recommendations, user_interactions), 3)
            },
            "anomalies": anomalies,
            "recommendations_count": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return report


class InteractionPatternAnalyzer:
    """Analyze user interaction patterns for anomaly detection"""
    
    def __init__(self):
        self.user_patterns = defaultdict(list)
        self.session_threshold = 3600  # 1 hour in seconds
    
    def detect_bot_behavior(self, user_interactions: List[Dict]) -> Tuple[bool, float]:
        """
        Detect suspicious bot-like behavior
        Returns (is_suspicious, confidence_score)
        """
        
        if len(user_interactions) < 5:
            return False, 0.0
        
        suspicious_indicators = 0
        total_checks = 0
        
        # Check 1: Interactions at regular intervals
        timestamps = sorted([i.get("timestamp") for i in user_interactions if i.get("timestamp")])
        if len(timestamps) > 2:
            intervals = []
            for i in range(1, len(timestamps)):
                try:
                    if isinstance(timestamps[i], str):
                        t1 = datetime.fromisoformat(timestamps[i-1])
                        t2 = datetime.fromisoformat(timestamps[i])
                    else:
                        t1 = timestamps[i-1]
                        t2 = timestamps[i]
                    
                    interval = (t2 - t1).total_seconds()
                    intervals.append(interval)
                except:
                    pass
            
            total_checks += 1
            if intervals:
                interval_std = np.std(intervals)
                if interval_std < 5 and np.mean(intervals) > 0:  # Very regular intervals
                    suspicious_indicators += 1
        
        # Check 2: Too many interactions in short time
        total_checks += 1
        hourly_interactions = len([i for i in user_interactions if isinstance(i.get("timestamp"), datetime)])
        if hourly_interactions > 50:  # More than 50 interactions per hour
            suspicious_indicators += 1
        
        # Check 3: Always same interaction type
        interaction_types = Counter(i.get("interaction_type") for i in user_interactions)
        total_checks += 1
        if len(interaction_types) == 1:  # Only one type of interaction
            suspicious_indicators += 1
        
        confidence = suspicious_indicators / total_checks if total_checks > 0 else 0.0
        is_suspicious = confidence > 0.66  # 2 out of 3 indicators
        
        return is_suspicious, confidence
    
    def get_user_session_info(self, user_interactions: List[Dict]) -> Dict:
        """Extract session information from user interactions"""
        
        if not user_interactions:
            return {"sessions": 0, "avg_session_duration": 0, "interactions_per_session": 0}
        
        sessions = []
        current_session = [user_interactions[0]]
        
        for interaction in user_interactions[1:]:
            try:
                t1 = current_session[-1].get("timestamp")
                t2 = interaction.get("timestamp")
                
                if isinstance(t1, str):
                    t1 = datetime.fromisoformat(t1)
                if isinstance(t2, str):
                    t2 = datetime.fromisoformat(t2)
                
                time_diff = (t2 - t1).total_seconds()
                
                if time_diff < self.session_threshold:
                    current_session.append(interaction)
                else:
                    sessions.append(current_session)
                    current_session = [interaction]
            except:
                current_session.append(interaction)
        
        if current_session:
            sessions.append(current_session)
        
        # Calculate metrics
        session_durations = []
        for session in sessions:
            if len(session) > 1:
                try:
                    start = session[0].get("timestamp")
                    end = session[-1].get("timestamp")
                    
                    if isinstance(start, str):
                        start = datetime.fromisoformat(start)
                    if isinstance(end, str):
                        end = datetime.fromisoformat(end)
                    
                    duration = (end - start).total_seconds()
                    session_durations.append(duration)
                except:
                    pass
        
        return {
            "sessions": len(sessions),
            "avg_session_duration": np.mean(session_durations) if session_durations else 0,
            "interactions_per_session": np.mean([len(s) for s in sessions]) if sessions else 0,
            "total_interactions": len(user_interactions)
        }


# Global instances
_quality_monitor = None
_pattern_analyzer = None


def get_quality_monitor() -> RecommendationQualityMonitor:
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = RecommendationQualityMonitor()
    return _quality_monitor


def get_pattern_analyzer() -> InteractionPatternAnalyzer:
    global _pattern_analyzer
    if _pattern_analyzer is None:
        _pattern_analyzer = InteractionPatternAnalyzer()
    return _pattern_analyzer
