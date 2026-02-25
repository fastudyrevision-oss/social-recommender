import { useState, useEffect } from 'react'

export default function Explore({ userId }) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('all')

  const categories = [
    { id: 'all', label: '✨ All', icon: '✨' },
    { id: 'tech', label: '💻 Tech', keywords: ['tech', 'ai', 'machine learning', 'coding'] },
    { id: 'photo', label: '📸 Photography', keywords: ['photo', 'sunset', 'landscape', 'camera'] },
    { id: 'food', label: '🍔 Food', keywords: ['food', 'recipe', 'cooking', 'eat'] },
    { id: 'fitness', label: '💪 Fitness', keywords: ['fitness', 'workout', 'gym', 'yoga'] },
    { id: 'travel', label: '✈️ Travel', keywords: ['travel', 'trip', 'adventure', 'explore'] },
  ]

  useEffect(() => {
    loadExplore()
  }, [userId, category])

  const loadExplore = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8000/feed/${userId}?limit=100`)
      if (!response.ok) throw new Error('Failed to load explore')
      const data = await response.json()
      
      let filteredPosts = data.feed || []

      if (category !== 'all') {
        const selectedCategory = categories.find(c => c.id === category)
        const keywords = selectedCategory?.keywords || []
        filteredPosts = filteredPosts.filter(post =>
          keywords.some(kw => post.content.toLowerCase().includes(kw))
        )
      }

      // Deduplicate posts by ID
      const seen = new Set()
      filteredPosts = filteredPosts.filter(post => {
        if (seen.has(post.id)) return false
        seen.add(post.id)
        return true
      })
      
      // Score posts by engagement and recency
      filteredPosts = filteredPosts.map(post => ({
        ...post,
        engagement_score: ((post.likes || 0) * 2 + (post.comments || 0) * 3 + (post.shares || 0) * 4)
      }))
      
      // Filter: only show posts with meaningful engagement (score >= 5)
      // This filters out low-quality posts with 0 engagement
      filteredPosts = filteredPosts.filter(post => post.engagement_score >= 5 || (post.likes || 0) > 0)
      
      // Sort by engagement score (highest first)
      filteredPosts.sort((a, b) => (b.engagement_score || 0) - (a.engagement_score || 0))
      setPosts(filteredPosts)
    } catch (error) {
      console.error('Failed to load explore:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="content-inner">
      {/* Header */}
      <div className="sticky top-0 z-40 pt-4 pb-4 mb-6" style={{ background: 'linear-gradient(180deg, rgba(10,14,39,1) 0%, rgba(10,14,39,0.8) 100%)' }}>
        <h1 className="text-3xl font-bold mb-4">🔥 Explore</h1>

        {/* Category Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`tag ${category === cat.id ? 'active' : ''}`}
              style={category === cat.id ? {
                background: 'linear-gradient(135deg, #ec4899, #8b5cf6)',
                border: 'none',
                color: 'white'
              } : {}}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Posts Grid */}
      {loading ? (
        <div className="flex-center py-10">
          <div className="text-secondary">Loading posts...</div>
        </div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">😔</div>
          <div className="empty-state-title">No posts in this category</div>
          <div className="empty-state-message">Try exploring other categories</div>
        </div>
      ) : (
        <div className="grid gap-4 pb-6">
          {posts.map((post) => (
            <div key={post.id} className="card interactive">
              {/* Post Header */}
              <div className="flex-between mb-4">
                <div className="flex gap-3 items-center">
                  <div 
                    className="w-10 h-10 rounded-full flex-center font-bold text-white"
                    style={{
                      background: `linear-gradient(135deg, #ec4899, #8b5cf6)`,
                    }}
                  >
                    {(post.author || 'U')[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-primary">{post.author || 'Unknown'}</p>
                  </div>
                </div>
                <span className="badge">
                  �� {post.recommendation_score?.toFixed(2) || '0.00'}
                </span>
              </div>

              {/* Post Content */}
              <p className="text-secondary mb-3 line-clamp-2">{post.content}</p>

              {/* Media Preview */}
              {post.media_url && (
                <div className="mb-4 rounded-lg overflow-hidden max-h-48 bg-black">
                  {post.media_type === 'video' ? (
                    <video
                      src={`http://localhost:8000${post.media_url}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <img
                      src={`http://localhost:8000${post.media_url}`}
                      alt="Post"
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
              )}

              {/* Post Stats */}
              <div className="flex gap-4 text-sm">
                <span className="badge">❤️ {post.likes || 0}</span>
                <span className="badge">💬 {post.comments || 0}</span>
                <span className="badge">↗️ {post.shares || 0}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
