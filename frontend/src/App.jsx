import { useState, useEffect } from 'react'
import Feed from './pages/Feed'
import Posts from './pages/Posts'
import Profile from './pages/Profile'
import Explore from './pages/Explore'
import Search from './pages/Search'
import Recommended from './pages/Recommended'
import './styles/premium.css'
import './App.enhanced.css'

function App() {
  const [activeView, setActiveView] = useState('feed')
  const [userId, setUserId] = useState(localStorage.getItem('userId') || 'user_' + Date.now())

  useEffect(() => {
    localStorage.setItem('userId', userId)
  }, [userId])

  return (
    <div className="app-container">
      {/* Main Content */}
      <div className="content-wrapper">
        {activeView === 'feed' && <Feed userId={userId} onNavigate={setActiveView} />}
        {activeView === 'posts' && <Posts userId={userId} />}
        {activeView === 'explore' && <Explore userId={userId} />}
        {activeView === 'search' && <Search userId={userId} />}
        {activeView === 'recommended' && <Recommended userId={userId} />}
        {activeView === 'profile' && <Profile userId={userId} />}
      </div>

      {/* Bottom Navigation Bar */}
      <nav className="navbar">
        <div className="navbar-content">
          <button
            onClick={() => setActiveView('feed')}
            className={`nav-button ${activeView === 'feed' ? 'active' : ''}`}
          >
            🏠 Feed
          </button>
          <button
            onClick={() => setActiveView('posts')}
            className={`nav-button ${activeView === 'posts' ? 'active' : ''}`}
          >
            ✍️ Posts
          </button>
          <button
            onClick={() => setActiveView('explore')}
            className={`nav-button ${activeView === 'explore' ? 'active' : ''}`}
          >
            🔥 Explore
          </button>
          <button
            onClick={() => setActiveView('recommended')}
            className={`nav-button ${activeView === 'recommended' ? 'active' : ''}`}
          >
            ✨ For You
          </button>
          <button
            onClick={() => setActiveView('search')}
            className={`nav-button ${activeView === 'search' ? 'active' : ''}`}
          >
            🔍 Search
          </button>
          <button
            onClick={() => setActiveView('profile')}
            className={`nav-button ${activeView === 'profile' ? 'active' : ''}`}
          >
            👤 Profile
          </button>
        </div>
      </nav>
    </div>
  )
}

export default App
