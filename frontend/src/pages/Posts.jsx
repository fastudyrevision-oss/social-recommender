import { useState, useEffect } from 'react'
import BehaviorTracker from '../components/BehaviorTracker'

export default function Posts({ userId }) {
  const [userPosts, setUserPosts] = useState([])
  const [caption, setCaption] = useState('')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({ posts: 0, likes: 0, comments: 0 })

  useEffect(() => {
    loadUserPosts()
  }, [userId])

  const loadUserPosts = () => {
    const posts = JSON.parse(localStorage.getItem(`userPosts_${userId}`) || '[]')
    
    // Calculate stats
    const totalLikes = posts.reduce((sum, p) => sum + (p.likes || 0), 0)
    const totalComments = posts.reduce((sum, p) => sum + (p.comments || 0), 0)
    
    setUserPosts(posts)
    setStats({
      posts: posts.length,
      likes: totalLikes,
      comments: totalComments
    })
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!caption.trim() && !file) return

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('caption', caption)
      formData.append('author', `User_${userId.slice(-6)}`)
      formData.append('user_id', userId)
      if (file) formData.append('file', file)

      const response = await fetch('http://localhost:8000/posts/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Upload failed')
      
      const newPost = {
        id: Date.now().toString(),
        content: caption,
        author: `User_${userId.slice(-6)}`,
        likes: 0,
        comments: 0,
        shares: 0,
        media_type: file ? (file.type.startsWith('video') ? 'video' : 'image') : null,
        media_url: file ? URL.createObjectURL(file) : null,
        created_at: new Date().toISOString()
      }
      
      const updated = [newPost, ...userPosts]
      setUserPosts(updated)
      localStorage.setItem(`userPosts_${userId}`, JSON.stringify(updated))

      setCaption('')
      setFile(null)
      
      // Track this as a share interaction
      trackInteraction(newPost.id, 'share')
      
      // Update stats
      loadUserPosts()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to upload post')
    } finally {
      setUploading(false)
    }
  }

  const deletePost = (postId) => {
    const updated = userPosts.filter(p => p.id !== postId)
    setUserPosts(updated)
    localStorage.setItem(`userPosts_${userId}`, JSON.stringify(updated))
    
    // Also delete from backend
    deletePostFromBackend(postId)
    
    loadUserPosts()
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
      {/* Behavior Tracker */}
      <BehaviorTracker userId={userId} />

      {/* Header */}
      <div className="sticky top-0 z-40 pt-4 pb-6 mb-6" style={{ background: 'linear-gradient(180deg, rgba(10,14,39,1) 0%, rgba(10,14,39,0.8) 100%)' }}>
        <h1 className="text-3xl font-bold mb-4">✍️ My Posts</h1>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-bg-tertiary rounded-lg p-3 text-center border border-border-color">
            <div className="text-2xl font-bold text-accent">{stats.posts}</div>
            <div className="text-xs text-tertiary">Posts</div>
          </div>
          <div className="bg-bg-tertiary rounded-lg p-3 text-center border border-border-color">
            <div className="text-2xl font-bold text-accent">❤️ {stats.likes}</div>
            <div className="text-xs text-tertiary">Likes</div>
          </div>
          <div className="bg-bg-tertiary rounded-lg p-3 text-center border border-border-color">
            <div className="text-2xl font-bold text-accent">💬 {stats.comments}</div>
            <div className="text-xs text-tertiary">Comments</div>
          </div>
        </div>
      </div>

      {/* Create Post Form */}
      <div className="card mb-6 border-2 border-accent border-opacity-30">
        <h2 className="text-xl font-bold text-accent mb-4">📝 Create New Post</h2>
        
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="What's on your mind?"
              className="input-field w-full h-32 resize-none"
            />
            <div className="text-xs text-tertiary mt-1">
              {caption.length} / 500 characters
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-primary mb-2">
              📎 Add Media (optional)
            </label>
            <input
              type="file"
              accept="image/*,video/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input-field w-full"
            />
            {file && (
              <div className="mt-3 p-3 bg-accent bg-opacity-10 rounded-lg flex items-center gap-2 border border-accent border-opacity-30">
                <span className="text-accent text-lg">✓</span>
                <span className="text-xs text-secondary flex-1 truncate">{file.name}</span>
                <span className="text-xs text-tertiary">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-4 border-t border-border-color">
            <button
              type="button"
              onClick={() => {
                setCaption('')
                setFile(null)
              }}
              className="btn btn-secondary flex-1"
            >
              Clear
            </button>
            <button
              type="submit"
              disabled={uploading || (!caption.trim() && !file)}
              className="btn btn-primary flex-1"
            >
              {uploading ? '⏳ Posting...' : '📤 Post'}
            </button>
          </div>
        </form>
      </div>

      {/* User Posts */}
      <div>
        <h2 className="text-xl font-bold text-primary mb-4">📸 Your Posts ({userPosts.length})</h2>

        {userPosts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <div className="empty-state-title">No posts yet</div>
            <div className="empty-state-message">Create your first post above!</div>
          </div>
        ) : (
          <div className="grid gap-4 pb-6">
            {userPosts.map((post) => (
              <div key={post.id} className="card hover:border-accent hover:border-opacity-50 transition-all">
                <div className="flex-between mb-4">
                  <div>
                    <p className="font-semibold text-primary">{post.author}</p>
                    <p className="text-xs text-tertiary">
                      {new Date(post.created_at).toLocaleDateString()} • {new Date(post.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <button
                    onClick={() => deletePost(post.id)}
                    className="btn btn-ghost text-red-500 hover:text-red-400"
                  >
                    🗑️
                  </button>
                </div>

                <p className="text-secondary mb-3 leading-relaxed">{post.content}</p>

                {post.media_url && (
                  <div className="mb-4 rounded-lg overflow-hidden max-h-96 bg-black">
                    {post.media_type === 'video' ? (
                      <video
                        src={post.media_url}
                        controls
                        className="w-full h-full"
                      />
                    ) : (
                      <img
                        src={post.media_url}
                        alt="Post media"
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                )}

                {/* Engagement Stats */}
                <div className="flex gap-6 text-sm text-tertiary border-t border-border-color pt-3">
                  <div className="flex items-center gap-2 hover:text-accent transition-colors cursor-pointer">
                    <span>❤️</span>
                    <span>{post.likes || 0} Likes</span>
                  </div>
                  <div className="flex items-center gap-2 hover:text-accent transition-colors cursor-pointer">
                    <span>💬</span>
                    <span>{post.comments || 0} Comments</span>
                  </div>
                  <div className="flex items-center gap-2 hover:text-accent transition-colors cursor-pointer">
                    <span>↗️</span>
                    <span>{post.shares || 0} Shares</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
