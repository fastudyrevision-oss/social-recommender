import { useState, useEffect } from 'react'

export default function Search({ userId }) {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchType, setSearchType] = useState('posts')
  const [recentSearches, setRecentSearches] = useState(
    JSON.parse(localStorage.getItem('recentSearches') || '[]')
  )

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return

    try {
      setLoading(true)
      
      // Add to recent searches
      const updated = [searchQuery, ...recentSearches.filter(s => s !== searchQuery)].slice(0, 5)
      setRecentSearches(updated)
      localStorage.setItem('recentSearches', JSON.stringify(updated))

      // Use semantic search via /recommend endpoint
      const response = await fetch('http://localhost:8000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, top_k: 20 })
      })

      if (!response.ok) throw new Error('Failed to search')
      
      const data = await response.json()
      let results = data.recommendations || []
      
      // Filter results: only show matches >= 10% (backend scores are very low due to exp(-distance/10) formula)
      results = results.filter(item => (item.similarity_score || 0) >= 0.1)
      
      // Deduplicate posts by ID
      const seen = new Set()
      results = results.filter(item => {
        if (seen.has(item.id)) return false
        seen.add(item.id)
        return true
      })

      if (searchType === 'users') {
        // Filter to unique users
        const users = new Map()
        results.forEach(post => {
          if (post.author && !users.has(post.author)) {
            users.set(post.author, post)
          }
        })
        results = Array.from(users.values())
      } else if (searchType === 'hashtags') {
        // Filter posts with hashtags
        results = results.filter(post => {
          const hashtags = (post.content?.match(/#\w+/g) || [])
          return hashtags.length > 0
        })
      }

      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
      alert('Search failed: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    handleSearch()
  }

  const handleRecentSearchClick = (term) => {
    setQuery(term)
    setTimeout(() => handleSearch(term), 100)
  }

  return (
    <div className="content-inner">
      {/* Search Header */}
      <div className="sticky top-0 z-40 pt-4 pb-4 mb-6" style={{ background: 'linear-gradient(180deg, rgba(10,14,39,1) 0%, rgba(10,14,39,0.8) 100%)' }}>
        <h1 className="text-3xl font-bold text-white mb-4">🔍 AI-Powered Search</h1>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="search-input-wrapper">
            <span className="search-input-icon">🔍</span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search with AI (try: machine learning, hiking, food recipes...)"
              className="input-field"
            />
            {query && (
              <button
                type="button"
                onClick={() => {
                  setQuery('')
                  setSearchResults([])
                }}
                className="search-input-clear"
              >
                ✕
              </button>
            )}
          </div>
        </form>

        {/* Search Type Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {['posts', 'users', 'hashtags'].map((type) => (
            <button
              key={type}
              onClick={() => {
                setSearchType(type)
                if (query) setTimeout(() => handleSearch(), 100)
              }}
              className={`tag ${searchType === type ? 'active' : ''}`}
              style={searchType === type ? {
                background: 'linear-gradient(135deg, #ec4899, #8b5cf6)',
                border: 'none',
                color: 'white'
              } : {}}
            >
              {type === 'posts' && '📝'} {type === 'users' && '👥'} {type === 'hashtags' && '#'}
              {' '} {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Results or Recent Searches */}
      <div className="pb-6">
        {query ? (
          <>
            <h2 className="text-xl font-bold text-white mb-6">
              {searchType === 'posts' && '📝 Posts'} 
              {searchType === 'users' && '👥 Users'} 
              {searchType === 'hashtags' && '# Hashtags'}
              {' '} ({searchResults.length})
            </h2>

            {loading ? (
              <div className="flex-center py-10">
                <div className="text-secondary">Searching with AI...</div>
              </div>
            ) : searchResults.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">�</div>
                <div className="empty-state-title">No high-quality matches found</div>
                <div className="empty-state-message">Try different search terms (we only show matches above 50% confidence)</div>
              </div>
            ) : (
              <div className="grid gap-4">
                {searchResults.map((item) => (
                  <div
                    key={item.id}
                    className="card interactive"
                  >
                    <div className="flex gap-4">
                      {/* Avatar */}
                      <div 
                        className="w-12 h-12 rounded-full flex-shrink-0 flex-center font-bold text-white"
                        style={{
                          background: `linear-gradient(135deg, #ec4899, #8b5cf6)`,
                        }}
                      >
                        {(item.author || 'U')[0].toUpperCase()}
                      </div>

                      {/* Content */}
                      <div className="flex-1">
                        <div className="flex-between mb-2">
                          <div className="font-semibold text-primary">{item.author || 'Unknown'}</div>
                          <div className="text-xs badge" style={{
                            background: `rgba(236, 72, 153, ${(item.similarity_score || 0) * 0.5})`,
                            color: '#ec4899'
                          }}>
                            🎯 {Math.round((item.similarity_score || 0) * 100)}% match
                          </div>
                        </div>
                        <p className="text-secondary text-sm line-clamp-2">{item.content}</p>
                        {item.media_type && (
                          <div className="mt-2 text-xs badge">
                            {item.media_type === 'video' ? '🎥 Video' : '🖼️ Image'}
                          </div>
                        )}
                        <div className="mt-2 flex gap-2 text-xs text-tertiary">
                          <span>❤️ {item.likes || 0}</span>
                          <span>💬 {item.comments || 0}</span>
                          <span>↗️ {item.shares || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            <h2 className="text-xl font-bold text-white mb-4">📌 Recent Searches</h2>
            {recentSearches.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">🕐</div>
                <div className="empty-state-title">No recent searches</div>
                <div className="empty-state-message">Your searches will appear here</div>
              </div>
            ) : (
              <div className="grid gap-2">
                {recentSearches.map((term, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleRecentSearchClick(term)}
                    className="card interactive text-left"
                  >
                    <div className="flex gap-3 items-center">
                      <span className="text-lg">🕐</span>
                      <span className="text-secondary">{term}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Search Tips */}
            <div className="mt-8">
              <h3 className="text-lg font-bold text-white mb-4">💡 Tips for Better Search</h3>
              <div className="grid gap-3">
                <div className="card">
                  <p className="text-secondary text-sm">
                    🔍 <strong>Semantic Search:</strong> Uses AI to understand meaning, not just keywords
                  </p>
                </div>
                <div className="card">
                  <p className="text-secondary text-sm">
                    �� <strong>Match Score:</strong> Shows how relevant each result is (0-100%)
                  </p>
                </div>
                <div className="card">
                  <p className="text-secondary text-sm">
                    💻 <strong>Examples:</strong> "machine learning", "hiking adventures", "cooking recipes"
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
