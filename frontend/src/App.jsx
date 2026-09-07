import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Profile from './pages/Profile'
import Pipeline from './pages/Pipeline'

const navItems = [
  { path: '/',         icon: '📊', label: 'Dashboard' },
  { path: '/jobs',     icon: '💼', label: 'Jobs'      },
  { path: '/profile',  icon: '👤', label: 'Profile'   },
  { path: '/pipeline', icon: '🤖', label: 'Pipeline'  },
]

export default function App() {
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🎯</div>
          <div>
            <h1>JobHunt AI</h1>
            <span>Daily Job Digest</span>
          </div>
        </div>

        <div className="nav-section-label">Navigation</div>
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}

        <div className="sidebar-footer">
          <p>Powered by</p>
          <strong>Groq · Llama 3.1 70B</strong>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <Routes>
          <Route path="/"         element={<Dashboard />} />
          <Route path="/jobs"     element={<Jobs />} />
          <Route path="/profile"  element={<Profile />} />
          <Route path="/pipeline" element={<Pipeline />} />
        </Routes>
      </main>
    </div>
  )
}
