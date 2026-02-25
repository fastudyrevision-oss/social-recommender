# Frontend Pages & Components Inventory

## Overview
**Total Pages:** 6  
**Total Standalone Components:** 7  
**Total Utilities:** 1  
**Navigation Type:** Bottom Navbar with 6 buttons

---

## MAIN PAGES (Shown in App.jsx Navigation) - 6 Pages

### 1. 🏠 Feed (`frontend/src/pages/Feed.jsx`)
**Navigation Button:** 🏠 Feed  
**Purpose:** Main social feed showing all posts  
**Features:**
- Load feed from `/feed/{user_id}` endpoint
- Display quality-scored posts (quality_score >= 10)
- Like, comment, share functionality
- Track user interactions (likes, comments, shares)
- Sort by quality score descending (best posts first)
- Shows user's own posts + feed posts

**Key State:**
- `posts` - Feed posts array
- `likedPosts` - Set of liked post IDs
- `loading` - Loading state

**Endpoints Used:**
- `GET /feed/{user_id}` - Fetch feed
- `POST /track/interaction` - Track likes/comments/shares

---

### 2. ✍️ Posts (`frontend/src/pages/Posts.jsx`)
**Navigation Button:** ✍️ Posts  
**Purpose:** Create and manage user's own posts  
**Features:**
- Create new post with optional media (image/video)
- Display user's posts with engagement stats
- Delete posts
- Track creation as "share" interaction
- Show total stats: posts, likes, comments
- Includes BehaviorTracker component
- Media upload with file validation

**Key State:**
- `userPosts` - User's created posts
- `caption` - Post text input
- `file` - Selected media file
- `uploading` - Upload progress
- `stats` - Engagement statistics

**Endpoints Used:**
- `POST /posts/upload` - Upload new post
- Uses localStorage for post persistence

---

### 3. 🔥 Explore (`frontend/src/pages/Explore.jsx`)
**Navigation Button:** 🔥 Explore  
**Purpose:** Browse posts by category  
**Features:**
- 6 category filters: All, Tech, Photography, Food, Fitness, Travel
- Keyword-based filtering
- Engagement scoring (likes*2 + comments*3 + shares*4)
- Minimum quality threshold (score >= 5 or likes > 0)
- Sort by engagement score
- Deduplication by post ID

**Key State:**
- `posts` - Filtered & scored posts
- `category` - Selected category
- `loading` - Loading state

**Endpoints Used:**
- `GET /feed/{user_id}?limit=100` - Fetch posts

---

### 4. ✨ For You (`frontend/src/pages/Recommended.jsx`)
**Navigation Button:** ✨ For You  
**Purpose:** AI-powered personalized recommendations  
**Features:**
- Behavior tracking analysis
- Category match scoring (40%)
- Author match scoring (30%)
- Engagement scoring (25%)
- Tag match scoring (10%)
- Recency boost (15 points for fresh posts)
- Minimum threshold: score >= 30
- Real-time updates every 2 seconds
- Shows reasoning behind recommendations
- Excludes already-interacted posts
- User insights: favorite categories, authors, interaction types

**Key State:**
- `recommendedPosts` - Top 5 scored posts
- `behaviors` - User interaction history
- `insights` - Calculated user preferences
- `loading` - Loading state

**Endpoints Used:**
- `GET /feed/{user_id}` - Fetch posts for scoring
- Uses localStorage for interaction tracking

---

### 5. 🔍 Search (`frontend/src/pages/Search.jsx`)
**Navigation Button:** 🔍 Search  
**Purpose:** Semantic search across posts  
**Features:**
- Query-based semantic search
- Filter by search type: posts, users, hashtags
- Similarity threshold filtering (>= 0.1)
- Deduplication by post ID
- User filtering (unique users only)
- Hashtag filtering (posts with #tags)
- Display match percentage (0-100%)
- Background opacity based on match score
- Recent searches tracking
- Quick search from recent list

**Key State:**
- `searchResults` - Filtered results
- `query` - Search input
- `searchType` - posts/users/hashtags
- `recentSearches` - Recent search history
- `loading` - Loading state

**Endpoints Used:**
- `POST /recommend` - Semantic search via recommender
- Field: `similarity_score` from backend

---

### 6. 👤 Profile (`frontend/src/pages/Profile.jsx`)
**Navigation Button:** 👤 Profile  
**Purpose:** User profile and analytics  
**Features:**
- Display user info (ID, avatar)
- Stats: posts, followers, following
- User's posts with engagement metrics
- Delete post functionality
- Media support (images/videos)
- Shows post creation date & time
- Engagement stats per post (likes, comments, shares)
- Includes BehaviorTracker component
- Posts sorted by engagement

**Key State:**
- `userPosts` - User's posts
- `stats` - User statistics
- `engagement` - Per-post engagement scores

**Endpoints Used:**
- Uses localStorage for all data

---

## STANDALONE COMPONENTS (Not in Main Nav) - 7 Components

### 1. InstagramFeed Component (`frontend/src/InstagramFeed.jsx`)
**Purpose:** Instagram-style feed component (may be unused in current routing)  
**Features:**
- Feed display with Instagram UI style
- Comments functionality
- Emoji reactions
- Post upload
- Interaction tracking
- Media support

**Status:** ⚠️ **NOT IN ACTIVE ROUTING** - No button in App.jsx navigation

---

### 2. SocialFeed Component (`frontend/src/SocialFeed.jsx`)
**Purpose:** Alternative social feed component (may be unused)  
**Features:**
- Feed display
- Post navigation (next/prev)
- Interaction tracking
- User analytics loading
- Engagement tracking

**Status:** ⚠️ **NOT IN ACTIVE ROUTING** - No button in App.jsx navigation

---

### 3. UserProfile Component (`frontend/src/UserProfile.jsx`)
**Purpose:** Alternative user profile (may be unused)  
**Features:**
- User analytics
- Preferences display
- Predictions display
- Stats dashboard

**Status:** ⚠️ **NOT IN ACTIVE ROUTING** - No button in App.jsx navigation

---

### 4. RecommendationUI Component (`frontend/src/RecommendationUI.jsx`)
**Purpose:** Standalone recommendation engine UI (may be unused)  
**Features:**
- Search query input
- Top K selection
- Recommendation display with match percentage
- Caching info
- System stats display

**Status:** ⚠️ **NOT IN ACTIVE ROUTING** - No button in App.jsx navigation

---

### 5. Comparison Component (`frontend/src/Comparison.jsx`)
**Purpose:** Comparison view (may be unused)  
**Features:** Unknown (not examined)

**Status:** ⚠️ **NOT IN ACTIVE ROUTING** - No button in App.jsx navigation

---

### 6. BehaviorTracker Component (`frontend/src/components/BehaviorTracker.jsx`)
**Purpose:** Track user interactions and update localStorage  
**Features:**
- Tracks all user behaviors (likes, views, comments, etc.)
- Real-time interaction logging
- localStorage persistence
- Used in: Posts.jsx, Profile.jsx, Recommended.jsx

**Status:** ✅ **IN USE** - Imported in multiple pages

---

### 7. Main App (`frontend/src/App.jsx`)
**Purpose:** Root component with navigation routing  
**Features:**
- Bottom navbar with 6 buttons
- State management for active view
- User ID management
- Conditional rendering based on activeView

**Status:** ✅ **ACTIVE** - Core routing logic

---

## UNUSED/ORPHANED COMPONENTS

### Components NOT in Main Navigation (4)
1. ❌ `InstagramFeed.jsx` - Standalone component, not routed
2. ❌ `SocialFeed.jsx` - Standalone component, not routed
3. ❌ `UserProfile.jsx` - Standalone component, not routed (different from Profile.jsx)
4. ❌ `RecommendationUI.jsx` - Standalone component, not routed
5. ❌ `Comparison.jsx` - Standalone component, not routed

**Recommendation:** Remove or repurpose these components if not used

---

## Page Feature Matrix

| Page | Feed | Upload | Comments | Reactions | Search | Analytics | Behavior Track | Media |
|------|------|--------|----------|-----------|--------|-----------|-----------------|-------|
| Feed | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Posts | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Explore | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| For You | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Search | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Profile | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## Navigation Flow

```
App (Root)
├── 🏠 Feed Page
│   └── onNavigate() → Posts
│
├── ✍️ Posts Page
│   └── BehaviorTracker
│
├── 🔥 Explore Page
│   └── Category filtering
│
├── ✨ For You (Recommended)
│   ├── BehaviorTracker
│   └── Real-time scoring
│
├── 🔍 Search Page
│   └── Semantic search
│
└── 👤 Profile Page
    └── BehaviorTracker
```

---

## Summary

### Active Pages (Shown to User)
✅ **6 Pages** - All accessible via bottom navbar

### Orphaned Components (Not Shown)
❌ **5 Components** - Can be removed:
- InstagramFeed.jsx
- SocialFeed.jsx
- UserProfile.jsx
- RecommendationUI.jsx
- Comparison.jsx

### Recommended Actions
1. **Remove orphaned components** if they're legacy/unused
2. **Consider consolidating** Feed, SocialFeed, and InstagramFeed into single component
3. **Consolidate** UserProfile with Profile page
4. **Integrate** RecommendationUI features into Search or For You pages

---

## File Structure

```
frontend/src/
├── App.jsx (MAIN - Routes 6 pages)
├── main.jsx
├── styles/
│   └── premium.css, etc.
├── pages/ (6 Active Pages)
│   ├── Feed.jsx ✅
│   ├── Posts.jsx ✅
│   ├── Explore.jsx ✅
│   ├── Recommended.jsx ✅
│   ├── Search.jsx ✅
│   └── Profile.jsx ✅
├── components/ (1 Utility)
│   └── BehaviorTracker.jsx ✅
└── [ORPHANED]
    ├── InstagramFeed.jsx ❌
    ├── SocialFeed.jsx ❌
    ├── UserProfile.jsx ❌
    ├── RecommendationUI.jsx ❌
    └── Comparison.jsx ❌
```
