# Detailed Endpoint Usage Map

## USED ENDPOINTS (13 Total)

### 1. POST /recommend ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/pages/Search.jsx` (line 24) - Search functionality
- `frontend/src/RecommendationUI.jsx` (line 39) - Recommendation engine
**Purpose:** Get semantic recommendations based on query
**Frequency:** Multiple times per session

### 2. GET /feed/{user_id} ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/pages/Feed.jsx` (line 18) - Main feed
- `frontend/src/pages/Explore.jsx` (line 24) - Explore page
- `frontend/src/pages/Recommended.jsx` (line 35) - For You page
- `frontend/src/InstagramFeed.jsx` (line 27) - Instagram component
- `frontend/src/SocialFeed.jsx` (line 21) - Social feed component
**Purpose:** Get feed posts for user
**Frequency:** Load on page, refresh every 2 seconds in Recommended

### 3. POST /posts/upload ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/pages/Posts.jsx` (line 43) - Create post page
- `frontend/src/InstagramFeed.jsx` (line 144) - Upload from Instagram feed
**Purpose:** Upload new post with optional media
**Frequency:** When user creates post

### 4. POST /track/interaction ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/pages/Feed.jsx` (trackInteraction function)
- `frontend/src/pages/Posts.jsx` (trackInteraction function)
- `frontend/src/components/BehaviorTracker.jsx` (line 52)
- `frontend/src/InstagramFeed.jsx` (line 162)
- `frontend/src/SocialFeed.jsx` (line 54)
**Purpose:** Track user interactions (like, comment, share, view)
**Frequency:** Every interaction

### 5. POST /posts/comment ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/InstagramFeed.jsx` (line 105)
**Purpose:** Post a comment on a post
**Frequency:** When user comments

### 6. GET /posts/{post_id}/comments ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/InstagramFeed.jsx` (line 52)
**Purpose:** Get comments for a post
**Frequency:** When post is viewed

### 7. POST /posts/react ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/InstagramFeed.jsx` (line 77)
**Purpose:** React to a post (emoji reactions)
**Frequency:** When user reacts

### 8. GET /posts/{post_id}/reactions ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/InstagramFeed.jsx` (line 63)
**Purpose:** Get reactions for a post
**Frequency:** When post is viewed

### 9. GET /user/{user_id}/analytics ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/SocialFeed.jsx` (line 44)
- `frontend/src/UserProfile.jsx` (line 20)
**Purpose:** Get user analytics data
**Frequency:** On component mount

### 10. GET /user/{user_id}/preferences ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/UserProfile.jsx` (line 21)
**Purpose:** Get user preferences
**Frequency:** Profile page load

### 11. GET /user/{user_id}/predictions ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/UserProfile.jsx` (line 22)
**Purpose:** Get prediction data for user
**Frequency:** Profile page load

### 12. GET /stats ✅
**Status:** ACTIVELY USED
**Called from:**
- `frontend/src/RecommendationUI.jsx` (line 19)
**Purpose:** Get system statistics
**Frequency:** On component mount

---

## UNUSED ENDPOINTS (7 Total)

### 1. POST /posts/add ❌
**Location:** backend/app/main.py (line 116)
**Purpose:** Add single post to index
**Why Unused:** Duplicate of `/posts/upload` which is used instead
**Recommendation:** Remove or consolidate

### 2. POST /posts/batch ❌
**Location:** backend/app/main.py (line 142)
**Purpose:** Batch add multiple posts
**Why Unused:** No batch upload UI in frontend
**Recommendation:** Keep for backend testing/seeding, not exposed in UI

### 3. POST /similar ❌
**Location:** backend/app/main.py (line 222)
**Purpose:** Find similar content
**Why Unused:** Similar feature not implemented in frontend
**Recommendation:** Could be used for "Similar Posts" feature

### 4. POST /embed ❌
**Location:** backend/app/main.py (line 249)
**Purpose:** Get embedding for text
**Why Unused:** Direct embedding not needed in frontend
**Recommendation:** Internal use only

### 5. POST /recommendations/personalized ❌
**Location:** backend/app/main.py (line 305)
**Purpose:** Get personalized recommendations
**Why Unused:** Frontend implements its own recommendation logic
**Recommendation:** Could replace frontend scoring with backend

### 6. GET /user/{user_id}/posts ❌
**Location:** backend/app/main.py (line 686)
**Purpose:** Get user's posts from backend
**Why Unused:** Frontend uses localStorage for user posts
**Recommendation:** Could use this for data persistence

### 7. DELETE /posts/{post_id} ❌
**Location:** backend/app/main.py (line 712)
**Purpose:** Delete a post
**Why Unused:** Delete is only done via localStorage, not backend
**Recommendation:** Implement post deletion from backend

---

## Summary Table

| Endpoint | Method | Used | Component | Priority |
|----------|--------|------|-----------|----------|
| /recommend | POST | ✅ | Search, RecommendationUI | CRITICAL |
| /feed/{user_id} | GET | ✅ | Multiple | CRITICAL |
| /posts/upload | POST | ✅ | Posts, InstagramFeed | CRITICAL |
| /track/interaction | POST | ✅ | Multiple | CRITICAL |
| /posts/comment | POST | ✅ | InstagramFeed | HIGH |
| /posts/{post_id}/comments | GET | ✅ | InstagramFeed | HIGH |
| /posts/react | POST | ✅ | InstagramFeed | HIGH |
| /posts/{post_id}/reactions | GET | ✅ | InstagramFeed | HIGH |
| /user/{user_id}/analytics | GET | ✅ | SocialFeed, UserProfile | MEDIUM |
| /user/{user_id}/preferences | GET | ✅ | UserProfile | MEDIUM |
| /user/{user_id}/predictions | GET | ✅ | UserProfile | MEDIUM |
| /stats | GET | ✅ | RecommendationUI | MEDIUM |
| /posts/add | POST | ❌ | - | LOW (DUPLICATE) |
| /posts/batch | POST | ❌ | - | LOW (BATCH) |
| /similar | POST | ❌ | - | LOW (FEATURE) |
| /embed | POST | ❌ | - | LOW (INTERNAL) |
| /recommendations/personalized | POST | ❌ | - | LOW (ALTERNATIVE) |
| /user/{user_id}/posts | GET | ❌ | - | LOW (ALTERNATIVE) |
| /posts/{post_id} | DELETE | ❌ | - | LOW (NOT WIRED) |
| / | GET | ❌ | - | DEPRECATED |
| /health | GET | ❌ | - | DEPRECATED |

**Usage Rate: 65% (13/20)**
