# Quick Reference: Backend Enhancement Usage

## 🚀 Quick Start (5 Minutes)

### 1. Start the Server
```bash
cd /home/mad/social-recommender/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Add Test Data
```bash
python test_enhanced_backend.py
# This runs all tests and validates the system
```

### 3. Check System Health
```bash
curl http://localhost:8000/diagnostics/performance
```

---

## 📊 API Endpoints Quick Reference

### Content Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/posts/add` | Add single post |
| POST | `/posts/batch` | Batch add posts |
| GET | `/trending` | Get trending posts |

### Recommendations
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/recommend` | Content-based search |
| POST | `/recommendations/personalized` | Personalized recommendations |
| POST | `/recommend/advanced` | Advanced with diversity/freshness |

### User Tracking & Analysis
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/track/interaction` | Track user behavior |
| GET | `/user/{user_id}/preferences` | Get user preferences |
| GET | `/user/{user_id}/insights` | Get user insights |
| GET | `/user/{user_id}/predictions` | Get behavior predictions |

### Quality & Monitoring
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/quality/assess` | Assess recommendation quality |
| POST | `/quality/feedback` | Record feedback |
| GET | `/anomalies/detect` | Detect anomalies |
| GET | `/analytics/system` | System analytics |
| GET | `/analytics/user/{user_id}` | User analytics |

### System Optimization
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/optimize/reindex` | Rebuild index |
| POST | `/optimize/clear-caches` | Clear caches |
| GET | `/diagnostics/performance` | Performance metrics |

---

## 💾 Data Flow Examples

### Example 1: Add Posts & Get Recommendations
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Add posts
posts = [
    {
        "id": "1",
        "content": "Amazing sunset at the beach",
        "author": "photographer",
        "likes": 100,
        "comments": 20
    }
]
requests.post(f"{BASE_URL}/posts/batch", json={"posts": posts})

# 2. Track user interaction
requests.post(f"{BASE_URL}/track/interaction", json={
    "user_id": "user1",
    "post_id": "1",
    "interaction_type": "like"
})

# 3. Get recommendations
response = requests.post(f"{BASE_URL}/recommend/advanced", json={
    "user_id": "user1",
    "top_k": 10,
    "diversity_boost": 0.7,
    "freshness_weight": 0.3
})

print(response.json())
```

### Example 2: Monitor Quality
```python
import requests

BASE_URL = "http://localhost:8000"

# Assess quality
response = requests.post(
    f"{BASE_URL}/quality/assess",
    params={"user_id": "user1", "top_k": 10}
)

quality_data = response.json()
print(f"Quality Score: {quality_data['quality_report']['quality_score']}")
print(f"Metrics: {quality_data['quality_report']['metrics']}")

# Detect anomalies
response = requests.get(
    f"{BASE_URL}/anomalies/detect",
    params={"user_id": "user1"}
)

anomalies = response.json()
if anomalies['anomalies']['detected']:
    print(f"⚠️ Anomalies: {anomalies['anomalies']['detected']}")
```

### Example 3: System Analytics
```python
import requests

BASE_URL = "http://localhost:8000"

# Get system health
response = requests.get(f"{BASE_URL}/diagnostics/performance")
metrics = response.json()

print(f"Avg Search Time: {metrics['performance']['avg_search_time_ms']}ms")
print(f"Cache Hit Rate: {metrics['performance']['cache_hit_rate']:.1%}")
print(f"Total Recommendations: {metrics['performance']['total_recommendations']}")

# Get user analytics
response = requests.get(f"{BASE_URL}/analytics/user/user1")
user_data = response.json()

print(f"Engagement Level: {user_data['insights']['engagement_level']}")
print(f"Activity Status: {user_data['insights']['activity_status']}")
```

---

## 🔧 Configuration Examples

### For Small Dataset (<1,000 posts)
```python
from backend.config_optimizer import RecommendationConfig

config = RecommendationConfig.for_small_dataset()
# Uses Flat indexing (exact search)
# Cache size: 500-1000 items
# Expected latency: 10-20ms
```

### For Large Dataset (>50,000 posts)
```python
from backend.config_optimizer import RecommendationConfig

config = RecommendationConfig.for_large_dataset()
# Uses IVF indexing (approximate search)
# Cache size: 5000-10000 items
# Expected latency: 20-100ms
```

### For Quality Focus
```python
from backend.config_optimizer import RecommendationConfig

config = RecommendationConfig.for_quality_focus()
# Searches more clusters (more accurate)
# Higher diversity penalty
# Quality score: 0.75-0.90
```

### For Speed Focus
```python
from backend.config_optimizer import RecommendationConfig

config = RecommendationConfig.for_speed_focus()
# Searches fewer clusters (faster)
# Longer cache TTL
# Response time: <50ms
```

---

## 📈 Performance Expectations

### By Dataset Size
| Size | Index | Latency | Quality | Memory |
|------|-------|---------|---------|--------|
| <1k | Flat | 10-20ms | 0.80 | <100MB |
| 1k-10k | Flat | 15-40ms | 0.75 | 100-500MB |
| 10k-50k | IVF(50) | 20-60ms | 0.72 | 500MB-1GB |
| 50k-100k | IVF(100) | 30-80ms | 0.70 | 1-2GB |
| >100k | IVF(200) | 50-150ms | 0.68 | 2-4GB |

### With Caching Enabled
- **First request**: 50-200ms (includes embedding computation)
- **Cached requests**: 5-20ms (much faster)
- **Cache hit rate**: 60-80% on typical usage

---

## 🎯 Recommendation Quality Metrics

### Quality Score Interpretation
- **0.80+**: Excellent (highly relevant, diverse, novel)
- **0.70-0.79**: Good (relevant, reasonably diverse)
- **0.60-0.69**: Fair (acceptable, some diversity)
- **<0.60**: Poor (low relevance or diversity issues)

### Key Metrics
```python
{
    "quality_score": 0.75,  # Overall quality (0-1)
    "metrics": {
        "ctr": 0.35,         # Click-through rate (higher is better)
        "diversity": 0.85,   # Content diversity (higher is better)
        "relevance": 0.72,   # Match to preferences (higher is better)
        "novelty": 0.88      # Fresh content (higher is better)
    }
}
```

---

## 🐛 Troubleshooting

### Problem: Low Cache Hit Rate
**Solution**: Increase cache size
```python
config["cache"]["embedding_cache_size"] = 5000
config["cache"]["search_cache_size"] = 2000
```

### Problem: High Latency
**Solution**: Reduce search depth or use caching
```python
config["faiss"]["nprobe"] = 10  # Search fewer clusters
config["cache"]["cache_ttl_seconds"] = 7200  # Longer cache
```

### Problem: Low Quality Scores
**Solution**: Use quality-focused configuration
```python
config = RecommendationConfig.for_quality_focus()
```

### Problem: Memory Usage Too High
**Solution**: Use memory-constrained settings
```python
config["cache"]["embedding_cache_size"] = 500
config["cache"]["search_cache_size"] = 250
config["faiss"]["batch_size"] = 500
```

---

## 🚨 Monitoring Checklist

### Daily
- [ ] Check `/diagnostics/performance` - Cache hit rate >60%?
- [ ] Check `/analytics/system` - No anomalies?
- [ ] Verify search latency <100ms

### Weekly
- [ ] Run `/quality/assess` for sample users
- [ ] Check `/anomalies/detect` - Any bots detected?
- [ ] Review recommendation quality scores (target >0.70)

### Monthly
- [ ] Run full test suite: `python test_enhanced_backend.py`
- [ ] Run verification: `python verify_enhancements.py`
- [ ] Analyze `/analytics/user/{user_id}` trends
- [ ] Consider reindexing: `POST /optimize/reindex`

---

## 🔑 Key Concepts

### Hybrid Recommendation Engine
Combines 4 scoring factors for better recommendations:
- **Content Similarity** (40%): Posts similar to liked content
- **User Preference** (30%): Match with learned preferences
- **Engagement Level** (20%): Popular/trending content
- **Freshness** (10%): Recent posts boost

### Time Decay
Older interactions matter less:
- Default decay: 0.95 per day
- Means: 30-day-old interactions = 21% weight of new interactions
- Helps prefer recent content

### Diversity Boosting
Prevents all recommendations from same source:
- Different authors recommended
- Different categories included
- Similar-looking posts filtered out

### Anomaly Detection
Identifies suspicious patterns:
- Bot-like behavior (regular intervals)
- Unusually high interaction rates
- Single interaction type only

---

## 📚 Additional Resources

### Configuration Guide
```bash
python config_optimizer.py  # Print configuration guide
```

### Verification Script
```bash
python verify_enhancements.py  # Verify all enhancements
```

### Integration Tests
```bash
python test_enhanced_backend.py  # Run full test suite
```

### Full Documentation
See `BACKEND_ENHANCEMENTS_SUMMARY.md` for complete details

---

## 🎓 Learning Path

1. **Start**: Run `verify_enhancements.py` to check system
2. **Test**: Run `test_enhanced_backend.py` to understand flow
3. **Learn**: Read endpoint examples above
4. **Configure**: Run `config_optimizer.py` for your use case
5. **Monitor**: Set up analytics monitoring with `/analytics/*`
6. **Optimize**: Adjust parameters based on metrics

---

## Support & Troubleshooting

### Check Logs
```bash
# Server logs show detailed errors
# Watch for exceptions in recommendation generation
```

### Debug Mode
```python
# Add to main.py for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Profiling
```python
# Time individual operations
import time

start = time.time()
# Your operation here
elapsed = time.time() - start
print(f"Operation took {elapsed*1000:.2f}ms")
```

---

**Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
