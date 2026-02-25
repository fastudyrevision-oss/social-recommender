import { useState, useEffect } from 'react'

export default function SimilarPosts({ postId, content, userId }) {
  const [similarPosts, setSimilarPosts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (postId && content) {
      loadSimilarPosts()
    }
  }, [postId, content])

  const loadSimilarPosts = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('Fetching similar posts for:', { postId, contentLength: content?.length })

      const response = await fetch('http://localhost:8000/similar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: content,
          top_k: 5,
          exclude_id: postId
        })
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to load similar posts: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      console.log('Similar posts response:', data)
      const posts = data.similar_posts || data.recommendations || []
      console.log('Parsed posts:', posts)
      setSimilarPosts(posts)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err)
      setError(errorMsg)
      console.error('Failed to load similar posts:', errorMsg)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="mt-6 p-4 bg-bg-tertiary rounded-lg">
        <div className="text-secondary text-sm">🔄 Loading similar posts...</div>
      </div>
    )
  }

  if (error || similarPosts.length === 0) {
    if (error) {
      return (
        <div className="mt-6 p-4 bg-red-500 bg-opacity-10 border border-red-500 rounded-lg">
          <div className="text-red-500 text-sm">❌ Error: {error}</div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-bold text-accent mb-4">🔗 Similar Posts</h3>
      <div className="grid gap-3">
        {similarPosts.map((post) => (
          <div
            key={post.id}
            className="card hover:border-accent hover:border-opacity-50 transition-all cursor-pointer"
          >
            <div className="flex gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-primary text-sm">{post.author || 'Unknown'}</p>
                <p className="text-secondary text-sm line-clamp-2">{post.content}</p>
                <div className="flex gap-2 mt-2 text-xs text-tertiary">
                  <span>❤️ {post.likes || 0}</span>
                  <span>💬 {post.comments || 0}</span>
                  <span>↗️ {post.shares || 0}</span>
                </div>
              </div>
              <div className="flex-shrink-0 text-right">
                <div className="text-sm font-bold text-accent">
                  {((post.similarity_score || 0) * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-tertiary">Match</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
