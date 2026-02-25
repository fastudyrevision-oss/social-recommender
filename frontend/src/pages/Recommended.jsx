import { useState, useEffect } from 'react'

export default function Recommended({ userId }) {
  const [recommendedPosts, setRecommendedPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [behaviors, setBehaviors] = useState([])
  const [insights, setInsights] = useState({
    favoriteCategories: [],
    favoriteAuthors: [],
    topInteractionType: 'likes',
    totalInteractions: 0
  })

  // Real-time tracking - updates whenever behavior changes
  useEffect(() => {
    const interval = setInterval(() => {
      loadAndRecommend()
    }, 2000) // Update every 2 seconds

    loadAndRecommend() // Initial load
    return () => clearInterval(interval)
  }, [userId])

  const loadAndRecommend = async () => {
    try {
      setLoading(true)

      // Load tracked behaviors from localStorage
      const storedInteractions = JSON.parse(
        localStorage.getItem(`interactions_${userId}`) || '[]'
      )
      setBehaviors(storedInteractions)

      // Load all posts
      const feedResponse = await fetch(`http://localhost:8000/feed/${userId}`)
      let allPosts = []
      if (feedResponse.ok) {
        const feedData = await feedResponse.json()
        allPosts = feedData.feed || []
      }

      // Load user's own posts
      const userPosts = JSON.parse(
        localStorage.getItem(`userPosts_${userId}`) || '[]'
      )
      allPosts = [...userPosts, ...allPosts]

      // Calculate behavior insights
      const insights = calculateInsights(storedInteractions, allPosts)
      setInsights(insights)

      // Score and recommend posts
      const scoredPosts = scoreAndRecommendPosts(
        allPosts,
        storedInteractions,
        insights
      )

      // Get top 5 recommended posts
      const top5 = scoredPosts.slice(0, 5)
      setRecommendedPosts(top5)
    } catch (error) {
      console.error('Failed to load recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateInsights = (interactions, allPosts) => {
    const interactions_by_type = {
      view: 0,
      like: 0,
      comment: 0,
      share: 0
    }

    const categories = {}
    const authors = {}

    interactions.forEach(interaction => {
      interactions_by_type[interaction.type] =
        (interactions_by_type[interaction.type] || 0) + 1

      // Find the post and get its metadata
      const post = allPosts.find(p => p.id === interaction.postId)
      if (post) {
        const category = post.metadata?.category || 'general'
        const author = post.author || 'unknown'

        categories[category] = (categories[category] || 0) + 1
        authors[author] = (authors[author] || 0) + 1
      }
    })

    // Get top categories
    const favoriteCategories = Object.entries(categories)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([cat]) => cat)

    // Get top authors
    const favoriteAuthors = Object.entries(authors)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([author]) => author)

    // Find most interacted type
    const topInteractionType = Object.entries(interactions_by_type).sort(
      ([, a], [, b]) => b - a
    )[0]?.[0] || 'likes'

    return {
      favoriteCategories,
      favoriteAuthors,
      topInteractionType,
      totalInteractions: interactions.length,
      interactionBreakdown: interactions_by_type
    }
  }

  const scoreAndRecommendPosts = (posts, interactions, insights) => {
    const interactedPostIds = new Set(
      interactions.map(i => i.postId)
    )

    const scored = posts
      .filter(post => !interactedPostIds.has(post.id)) // Don't recommend already interacted posts
      .map(post => {
        let score = 0
        let reasons = []

        // Base score for being in the system
        score += 10

        // Score based on category match (40%)
        if (
          insights.favoriteCategories.includes(
            post.metadata?.category || ''
          )
        ) {
          score += 40
          reasons.push(`📂 Matches your favorite: ${post.metadata.category}`)
        }

        // Score based on author match (30%)
        if (insights.favoriteAuthors.includes(post.author)) {
          score += 30
          reasons.push(`👤 From favorite author: ${post.author}`)
        }

        // Score based on engagement (25%)
        const engagement = (post.likes || 0) + (post.comments || 0) * 2 + (post.shares || 0) * 3
        if (engagement > 100) {
          score += 25
          reasons.push(`🔥 Highly engaged: ${engagement} interactions`)
        } else if (engagement > 50) {
          score += 20
          reasons.push(`🌟 Popular: ${engagement} interactions`)
        } else if (engagement > 20) {
          score += 15
          reasons.push(`⭐ Good engagement: ${engagement} interactions`)
        } else if (engagement > 0) {
          score += 10
        }

        // Score based on tags match (10%)
        const tags = post.metadata?.tags || []
        if (tags.some(tag =>
          interactions.some(i => {
            const interactPost = posts.find(p => p.id === i.postId)
            return interactPost?.metadata?.tags?.some(t =>
              t.toLowerCase() === tag.toLowerCase()
            )
          })
        )) {
          score += 10
          reasons.push('🏷️ Related to your interests')
        }

        // Recency boost (max 15 points for fresh posts)
        if (post.created_at) {
          const hoursOld = (Date.now() - new Date(post.created_at).getTime()) / (1000 * 60 * 60)
          if (hoursOld < 24) {
            score += 15 * (1 - hoursOld / 24) // Max 15 if posted today, decays to 0 after 24h
            reasons.push('📅 Fresh post')
          }
        }

        return {
          ...post,
          score,
          reasons: reasons.length > 0 ? reasons : ['✨ Similar to your activity']
        }
      })
      .filter(post => post.score >= 30) // Raise threshold to 30 to show only good quality matches
      .sort((a, b) => b.score - a.score) // Sort by score descending (highest first)

    return scored
  }

  const trackInteraction = (postId, type) => {
    const interaction = {
      id: Date.now(),
      postId,
      type,
      timestamp: new Date().toISOString()
    }

    const stored = JSON.parse(
      localStorage.getItem(`interactions_${userId}`) || '[]'
    )
    const updated = [interaction, ...stored].slice(0, 50)
    localStorage.setItem(`interactions_${userId}`, JSON.stringify(updated))
  }

  return (
    <div className="content-inner">
      {/* Header */}
      <div
        className="sticky top-0 z-40 pt-4 pb-6 mb-6"
        style={{
          background:
            'linear-gradient(180deg, rgba(10,14,39,1) 0%, rgba(10,14,39,0.8) 100%)'
        }}
      >
        <h1 className="text-3xl font-bold mb-2">✨ Recommended For You</h1>
        <p className="text-secondary text-sm">
          Based on {insights.totalInteractions} of your interactions
        </p>
      </div>

      {/* Insights Card */}
      {insights.totalInteractions > 0 && (
        <div className="card mb-6 border border-accent border-opacity-30">
          <h3 className="text-lg font-bold text-accent mb-4">📊 Your Profile</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="p-3 bg-bg-tertiary rounded-lg">
              <p className="text-2xl font-bold text-accent">
                {insights.totalInteractions}
              </p>
              <p className="text-xs text-tertiary">Total interactions</p>
            </div>
            <div className="p-3 bg-bg-tertiary rounded-lg">
              <p className="text-2xl font-bold text-accent">
                {insights.interactionBreakdown?.like || 0}
              </p>
              <p className="text-xs text-tertiary">❤️ Likes</p>
            </div>
            <div className="p-3 bg-bg-tertiary rounded-lg">
              <p className="text-2xl font-bold text-accent">
                {insights.interactionBreakdown?.comment || 0}
              </p>
              <p className="text-xs text-tertiary">💬 Comments</p>
            </div>
            <div className="p-3 bg-bg-tertiary rounded-lg">
              <p className="text-2xl font-bold text-accent">
                {insights.interactionBreakdown?.share || 0}
              </p>
              <p className="text-xs text-tertiary">↗️ Shares</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <div>
              <p className="text-xs text-tertiary mb-2">Favorite Categories:</p>
              <div className="flex gap-2 flex-wrap">
                {insights.favoriteCategories.length > 0 ? (
                  insights.favoriteCategories.map(cat => (
                    <span key={cat} className="tag active">
                      📂 {cat}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-tertiary">No data yet</span>
                )}
              </div>
            </div>
          </div>

          {insights.favoriteAuthors.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-tertiary mb-2">Favorite Authors:</p>
              <div className="flex gap-2 flex-wrap">
                {insights.favoriteAuthors.map(author => (
                  <span key={author} className="tag">
                    👤 {author}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {loading && insights.totalInteractions === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🎯</div>
          <div className="empty-state-title">Start Interacting</div>
          <div className="empty-state-message">
            Like, comment, and share posts to get personalized recommendations
          </div>
        </div>
      ) : recommendedPosts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🎉</div>
          <div className="empty-state-title">You've Seen Everything!</div>
          <div className="empty-state-message">
            Keep interacting with more posts to discover new recommendations
          </div>
        </div>
      ) : (
        <div className="space-y-4 pb-6">
          <h2 className="text-xl font-bold text-white">
            🏆 Top 5 Recommended Posts
          </h2>

          {recommendedPosts.map((post, index) => (
            <div key={post.id} className="card">
              {/* Rank Badge */}
              <div className="absolute top-4 right-4">
                <div
                  className="w-8 h-8 rounded-full flex-center font-bold text-white text-sm"
                  style={{
                    background: `linear-gradient(135deg, #ec4899, #8b5cf6)`
                  }}
                >
                  #{index + 1}
                </div>
              </div>

              {/* Post Header */}
              <div className="flex-between mb-4">
                <div className="flex gap-3 items-center">
                  <div
                    className="w-10 h-10 rounded-full flex-center font-bold text-white"
                    style={{
                      background: `linear-gradient(135deg, #ec4899, #8b5cf6)`
                    }}
                  >
                    {(post.author || 'U')[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-primary">
                      {post.author || 'Unknown'}
                    </p>
                    <p className="text-xs text-tertiary">
                      {post.metadata?.category && `📂 ${post.metadata.category}`}
                    </p>
                  </div>
                </div>
                {post.score && (
                  <div
                    className="text-sm font-bold px-3 py-1 rounded-lg"
                    style={{
                      background: `rgba(236, 72, 153, 0.2)`,
                      color: '#ec4899'
                    }}
                  >
                    {Math.round(post.score)}% match
                  </div>
                )}
              </div>

              {/* Why Recommended */}
              <div className="mb-3 p-3 bg-bg-tertiary rounded-lg border-l-2 border-accent">
                <p className="text-xs text-tertiary mb-2">Why recommended:</p>
                <div className="flex flex-wrap gap-2">
                  {post.reasons &&
                    post.reasons.map((reason, i) => (
                      <span key={i} className="text-xs text-accent">
                        {reason}
                      </span>
                    ))}
                </div>
              </div>

              {/* Post Content */}
              <p className="text-secondary mb-3">{post.content}</p>

              {/* Media */}
              {post.media_url && (
                <div className="mb-4 rounded-lg overflow-hidden max-h-96 bg-black">
                  {post.media_type === 'video' ? (
                    <video
                      src={
                        post.media_url.startsWith('blob:')
                          ? post.media_url
                          : `http://localhost:8000${post.media_url}`
                      }
                      controls
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <img
                      src={
                        post.media_url.startsWith('blob:')
                          ? post.media_url
                          : `http://localhost:8000${post.media_url}`
                      }
                      alt="Post"
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
              )}

              {/* Tags */}
              {post.metadata?.tags && post.metadata.tags.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-2">
                  {post.metadata.tags.map((tag, i) => (
                    <span key={i} className="text-xs badge">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Engagement Stats */}
              <div className="flex gap-4 pt-4 border-t border-border-color">
                <button
                  onClick={() => trackInteraction(post.id, 'like')}
                  className="flex-1 btn btn-ghost flex-center gap-2"
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
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Live Update Indicator */}
      {insights.totalInteractions > 0 && recommendedPosts.length > 0 && (
        <div className="fixed bottom-6 right-6 p-3 bg-accent rounded-lg text-white text-xs flex items-center gap-2">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          Live Updates Enabled
        </div>
      )}
    </div>
  )
}
