import { useState, useEffect } from 'react'
import BehaviorTracker from '../components/BehaviorTracker'

export default function Profile({ userId }) {
  const [userPosts, setUserPosts] = useState([])
  const [stats, setStats] = useState({ posts: 0, followers: 0, following: 0 })

  useEffect(() => {
    loadUserProfile()
  }, [userId])

  const loadUserProfile = () => {
    let posts = JSON.parse(localStorage.getItem(`userPosts_${userId}`) || '[]')
    
    // Score user's own posts by engagement
    posts = posts.map(post => ({
      ...post,
      engagement: (post.likes || 0) + (post.comments || 0) * 2 + (post.shares || 0) * 3
    }))
    
    // Sort by engagement (best performing posts first)
    posts.sort((a, b) => (b.engagement || 0) - (a.engagement || 0))
    
    setUserPosts(posts)
    setStats({
      posts: posts.length,
      followers: Math.floor(Math.random() * 1000),
      following: Math.floor(Math.random() * 500)
    })
  }

  const deletePost = (postId) => {
    const updated = userPosts.filter(p => p.id !== postId)
    setUserPosts(updated)
    localStorage.setItem(`userPosts_${userId}`, JSON.stringify(updated))
    
    // Also delete from backend
    deletePostFromBackend(postId)
    
    loadUserProfile()
  }

  const deletePostFromBackend = async (postId) => {
    try {
      const response = await fetch(`http://localhost:8000/posts/${postId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        console.log(`✅ Post ${postId} deleted from backend`)
      } else {
        console.warn(`⚠️ Failed to delete from backend: ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to delete post from backend:', error)
    }
  }

  return (
    <div className="content-inner">
      {/* Behavior Tracker */}
      <BehaviorTracker userId={userId} />
      {/* Profile Header */}
      <div className="card mb-6">
        <div className="flex gap-4 mb-4">
          <div 
            className="w-16 h-16 rounded-full flex-center font-bold text-white text-2xl flex-shrink-0"
            style={{
              background: `linear-gradient(135deg, #ec4899, #8b5cf6)`,
            }}
          >
            {userId.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-primary">User_{userId.slice(-6)}</h1>
            <p className="text-secondary">ID: {userId}</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-bg-tertiary rounded-lg">
            <p className="text-2xl font-bold text-accent">{stats.posts}</p>
            <p className="text-xs text-tertiary">Posts</p>
          </div>
          <div className="text-center p-3 bg-bg-tertiary rounded-lg">
            <p className="text-2xl font-bold text-accent">{stats.followers}</p>
            <p className="text-xs text-tertiary">Followers</p>
          </div>
          <div className="text-center p-3 bg-bg-tertiary rounded-lg">
            <p className="text-2xl font-bold text-accent">{stats.following}</p>
            <p className="text-xs text-tertiary">Following</p>
          </div>
        </div>
      </div>

      {/* User Posts */}
      <h2 className="text-xl font-bold text-primary mb-4">📸 My Posts ({userPosts.length})</h2>

      {userPosts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <div className="empty-state-title">No posts yet</div>
          <div className="empty-state-message">Go to Feed and create your first post!</div>
        </div>
      ) : (
        <div className="grid gap-4 pb-6">
          {userPosts.map((post) => (
            <div key={post.id} className="card">
              <div className="flex-between mb-4">
                <div>
                  <p className="font-semibold text-primary">{post.author}</p>
                  <p className="text-xs text-tertiary">{new Date(post.created_at).toLocaleDateString()}</p>
                </div>
                <button
                  onClick={() => deletePost(post.id)}
                  className="btn btn-ghost text-red-500"
                >
                  🗑️
                </button>
              </div>

              <p className="text-secondary mb-3">{post.content}</p>

              {post.media_url && (
                <div className="mb-4 rounded-lg overflow-hidden max-h-96 bg-black">
                  {post.media_type === 'video' ? (
                    <video
                      src={post.media_url}
                      controls
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <img
                      src={post.media_url}
                      alt="Post"
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
              )}

              <div className="flex gap-4 pt-4 border-t border-border-color">
                <button className="flex-1 btn btn-ghost flex-center gap-2">
                  ❤️ {post.likes || 0}
                </button>
                <button className="flex-1 btn btn-ghost flex-center gap-2">
                  💬 {post.comments || 0}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
