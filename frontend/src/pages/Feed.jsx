import { useState, useEffect } from 'react'
import SimilarPosts from '../components/SimilarPosts'

export default function Feed({ userId, onNavigate }) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [userPosts, setUserPosts] = useState([])
  const [expandedPost, setExpandedPost] = useState(null)
  const [likedPosts, setLikedPosts] = useState(
    JSON.parse(localStorage.getItem(`likedPosts_${userId}`) || '[]')
  )

  useEffect(() => {
    loadFeed()
  }, [userId])

  const loadFeed = async () => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8000/feed/${userId}`)
      if (!response.ok) throw new Error('Failed to load feed')
      const data = await response.json()
      
      let feedPosts = data.feed || []
      
      // Load user behavior tracking from localStorage
      const storedInteractions = JSON.parse(
        localStorage.getItem(`interactions_${userId}`) || '[]'
      )
      
      // Get user's interaction history
      const interactedPostIds = new Set(
        storedInteractions.map(i => i.postId)
      )
      
      // Score posts based on engagement and behavior match
      feedPosts = feedPosts.map(post => {
        let score = 0
        
        // Base engagement score (likes + comments * 1.5 + shares * 2)
        score += (post.likes || 0) + (post.comments || 0) * 1.5 + (post.shares || 0) * 2
        
        // If user interacted with similar posts, boost score
        if (interactedPostIds.has(post.id)) {
          score += 50 // Already engaged posts score higher
        }
        
        return {
          ...post,
          quality_score: score
        }
      })
      
      // Filter: only show posts with quality_score >= 10 or freshly added posts
      feedPosts = feedPosts.filter(post => post.quality_score >= 10 || (post.likes || 0) > 0)
      
      // Sort by quality score descending (best first)
      feedPosts.sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0))
      
      setPosts(feedPosts)

      const userPostsFromStorage = JSON.parse(localStorage.getItem(`userPosts_${userId}`) || '[]')
      setUserPosts(userPostsFromStorage)
    } catch (error) {
      console.error('Failed to load feed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLike = (postId) => {
    setPosts(posts.map(p =>
      p.id === postId ? { ...p, likes: (p.likes || 0) + 1 } : p
    ))

    if (!likedPosts.includes(postId)) {
      const updated = [...likedPosts, postId]
      setLikedPosts(updated)
      localStorage.setItem(`likedPosts_${userId}`, JSON.stringify(updated))
      trackInteraction(postId, 'like')
    }
  }

  const trackInteraction = (postId, type) => {
    const interaction = {
      id: Date.now(),
      postId,
      type,
      timestamp: new Date().toISOString()
    }

    const stored = JSON.parse(localStorage.getItem(`interactions_${userId}`) || '[]')
    const updated = [interaction, ...stored].slice(0, 50)
    localStorage.setItem(`interactions_${userId}`, JSON.stringify(updated))
  }

  return (
    <div className="content-inner">
      {/* Header */}
      <div className="sticky top-0 z-40 pt-4 pb-4 mb-6" style={{ background: 'linear-gradient(180deg, rgba(10,14,39,1) 0%, rgba(10,14,39,0.8) 100%)' }}>
        <div className="flex-between">
          <h1 className="text-3xl font-bold">🏠 Feed</h1>
          <button
            onClick={() => onNavigate && onNavigate('posts')}
            className="btn btn-primary"
          >
            ➕ Post
          </button>
        </div>
      </div>

      {/* Feed */}
      {loading ? (
        <div className="flex-center py-10">
          <div className="text-secondary">Loading feed...</div>
        </div>
      ) : posts.length === 0 && userPosts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <div className="empty-state-title">No posts yet</div>
          <div className="empty-state-message">Be the first to share something!</div>
        </div>
      ) : (
        <div className="grid gap-4 pb-6">
          {[...userPosts, ...posts].map((post) => (
            <div key={post.id} className="card">
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
                    <p className="text-xs text-tertiary">{new Date(post.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>

              <p className="text-secondary mb-3">{post.content}</p>

              {post.media_url && (
                <div className="mb-4 rounded-lg overflow-hidden max-h-96 bg-black">
                  {post.media_type === 'video' ? (
                    <video
                      src={post.media_url.startsWith('blob:') ? post.media_url : `http://localhost:8000${post.media_url}`}
                      controls
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <img
                      src={post.media_url.startsWith('blob:') ? post.media_url : `http://localhost:8000${post.media_url}`}
                      alt="Post"
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
              )}

              <div className="flex gap-4 pt-4 border-t border-border-color">
                <button
                  onClick={() => handleLike(post.id)}
                  disabled={likedPosts.includes(post.id)}
                  className={`flex-1 btn ${likedPosts.includes(post.id) ? 'btn-primary' : 'btn-ghost'} flex-center gap-2`}
                >
                  ❤️ {post.likes || 0}
                </button>
                <button 
                  onClick={() => trackInteraction(post.id, 'comment')}
                  className="flex-1 btn btn-ghost flex-center gap-2"
                >
                  💬 {post.comments || 0}
                </button>
                <button
                  onClick={() => trackInteraction(post.id, 'share')}
                  className="flex-1 btn btn-ghost flex-center gap-2"
                >
                  ↗️ {post.shares || 0}
                </button>
                <button
                  onClick={() => setExpandedPost(expandedPost === post.id ? null : post.id)}
                  className="flex-1 btn btn-ghost flex-center gap-2"
                >
                  🔗 Similar
                </button>
              </div>

              {expandedPost === post.id && (
                <SimilarPosts 
                  postId={post.id}
                  content={post.content}
                  userId={userId}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
