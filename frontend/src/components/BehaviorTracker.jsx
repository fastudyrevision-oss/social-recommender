import { useState, useEffect } from 'react'

export default function BehaviorTracker({ userId }) {
  const [interactions, setInteractions] = useState([])
  const [stats, setStats] = useState({
    totalViews: 0,
    totalLikes: 0,
    totalComments: 0,
    totalShares: 0,
    topCategory: 'N/A',
    engagementRate: 0
  })

  useEffect(() => {
    loadBehaviorData()
    const interval = setInterval(loadBehaviorData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [userId])

  const loadBehaviorData = () => {
    const stored = JSON.parse(localStorage.getItem(`interactions_${userId}`) || '[]')
    setInteractions(stored)

    // Calculate stats
    const stats = {
      totalViews: stored.filter(i => i.type === 'view').length,
      totalLikes: stored.filter(i => i.type === 'like').length,
      totalComments: stored.filter(i => i.type === 'comment').length,
      totalShares: stored.filter(i => i.type === 'share').length,
      topCategory: 'Technology', // Could be calculated
      engagementRate: stored.length > 0 ? Math.min(Math.round((stored.length / 100) * 100), 100) : 0
    }
    setStats(stats)
  }

  const trackInteraction = (postId, type) => {
    const interaction = {
      id: Date.now(),
      postId,
      type,
      timestamp: new Date().toISOString()
    }

    const updated = [interaction, ...interactions].slice(0, 50) // Keep last 50
    setInteractions(updated)
    localStorage.setItem(`interactions_${userId}`, JSON.stringify(updated))

    // Update stats
    loadBehaviorData()

    // Send to backend if desired
    fetch('http://localhost:8000/track/interaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        post_id: postId,
        interaction_type: type,
        timestamp: interaction.timestamp
      })
    }).catch(e => console.log('Backend tracking:', e))
  }

  return (
    <div className="card mb-6">
      <h3 className="text-lg font-bold text-white mb-4">📊 Behavior Tracking</h3>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="p-3 bg-bg-tertiary rounded-lg text-center">
          <p className="text-2xl font-bold text-accent">{stats.totalViews}</p>
          <p className="text-xs text-tertiary">👁️ Views</p>
        </div>
        <div className="p-3 bg-bg-tertiary rounded-lg text-center">
          <p className="text-2xl font-bold text-accent">{stats.totalLikes}</p>
          <p className="text-xs text-tertiary">❤️ Likes</p>
        </div>
        <div className="p-3 bg-bg-tertiary rounded-lg text-center">
          <p className="text-2xl font-bold text-accent">{stats.totalComments}</p>
          <p className="text-xs text-tertiary">💬 Comments</p>
        </div>
        <div className="p-3 bg-bg-tertiary rounded-lg text-center">
          <p className="text-2xl font-bold text-accent">{stats.totalShares}</p>
          <p className="text-xs text-tertiary">↗️ Shares</p>
        </div>
      </div>

      {/* Engagement Rate */}
      <div className="mb-6">
        <div className="flex-between mb-2">
          <span className="text-sm font-semibold text-secondary">Engagement Rate</span>
          <span className="text-sm font-bold text-accent">{stats.engagementRate}%</span>
        </div>
        <div className="w-full bg-bg-tertiary rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all"
            style={{
              width: `${stats.engagementRate}%`,
              background: 'linear-gradient(90deg, #ec4899, #8b5cf6)'
            }}
          />
        </div>
      </div>

      {/* Recent Interactions */}
      {interactions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-secondary mb-2">🔔 Recent Activity</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {interactions.slice(0, 10).map((int) => (
              <div
                key={int.id}
                className="text-xs flex-between p-2 bg-bg-tertiary rounded-lg"
              >
                <span className="text-tertiary">{int.timestamp.split('T')[1].slice(0, 5)}</span>
                <span className="text-secondary">
                  {int.type === 'view' && '👁️'} 
                  {int.type === 'like' && '❤️'} 
                  {int.type === 'comment' && '💬'} 
                  {int.type === 'share' && '↗️'} 
                  {' '} {int.type.charAt(0).toUpperCase() + int.type.slice(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {interactions.length === 0 && (
        <p className="text-sm text-tertiary text-center py-4">
          👋 No interactions yet. Like, comment, or share posts to start tracking!
        </p>
      )}

      {/* Info */}
      <div className="mt-4 p-3 bg-bg-tertiary rounded-lg border-l-2" style={{ borderColor: '#ec4899' }}>
        <p className="text-xs text-secondary">
          ℹ️ <strong>How it works:</strong> Your interactions (likes, comments, shares) are tracked to personalize recommendations
        </p>
      </div>
    </div>
  )
}
