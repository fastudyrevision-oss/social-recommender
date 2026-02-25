/**
 * PostSync Utility - Synchronize posts between localStorage and backend
 * Uses GET /user/{user_id}/posts to fetch user posts from backend
 */

export const postSync = {
  /**
   * Get user's posts from backend
   */
  async getUserPosts(userId, limit = 50) {
    try {
      const response = await fetch(`http://localhost:8000/user/${userId}/posts?limit=${limit}`)
      
      if (!response.ok) {
        console.warn(`Failed to fetch posts from backend: ${response.status}`)
        return null
      }

      const data = await response.json()
      return data.posts || []
    } catch (error) {
      console.error('Failed to get user posts from backend:', error)
      return null
    }
  },

  /**
   * Sync posts: prefer backend if available, fallback to localStorage
   */
  async syncUserPosts(userId) {
    // Try to get from backend
    const backendPosts = await this.getUserPosts(userId)
    
    if (backendPosts && backendPosts.length > 0) {
      // Save backend posts to localStorage for offline access
      localStorage.setItem(`userPosts_${userId}`, JSON.stringify(backendPosts))
      console.log(`✅ Synced ${backendPosts.length} posts from backend`)
      return backendPosts
    }
    
    // Fallback to localStorage
    const storedPosts = JSON.parse(localStorage.getItem(`userPosts_${userId}`) || '[]')
    return storedPosts
  },

  /**
   * Check if posts are synced
   */
  async checkSync(userId) {
    const backendPosts = await this.getUserPosts(userId)
    const localPosts = JSON.parse(localStorage.getItem(`userPosts_${userId}`) || '[]')
    
    if (!backendPosts) {
      return {
        synced: false,
        backend: 0,
        local: localPosts.length,
        message: '⚠️ Backend unavailable, using local posts'
      }
    }

    const synced = JSON.stringify(backendPosts.sort(p => p.id)) === 
                   JSON.stringify(localPosts.sort(p => p.id))
    
    return {
      synced,
      backend: backendPosts.length,
      local: localPosts.length,
      message: synced ? '✅ Posts synced' : '⚠️ Posts out of sync'
    }
  }
}
