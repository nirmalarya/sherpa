import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Mountain } from 'lucide-react'

// Pages
import HomePage from './pages/HomePage'
import SessionsPage from './pages/SessionsPage'
import SessionDetailPage from './pages/SessionDetailPage'
// import KnowledgePage from './pages/KnowledgePage'
// import SourcesPage from './pages/SourcesPage'

// Placeholder pages
function KnowledgePage() {
  return <div className="p-8"><h1 className="text-3xl font-bold">Knowledge Page - Coming Soon</h1></div>
}
function SourcesPage() {
  return <div className="p-8"><h1 className="text-3xl font-bold">Sources Page - Coming Soon</h1></div>
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        {/* Navigation */}
        <nav className="bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link to="/" className="flex items-center">
                  <Mountain className="h-8 w-8 text-primary-600" />
                  <span className="ml-2 text-xl font-bold text-gray-900">SHERPA V1</span>
                </Link>
                <div className="ml-10 flex items-center space-x-4">
                  <Link to="/" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                    Home
                  </Link>
                  <Link to="/sessions" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                    Sessions
                  </Link>
                  <Link to="/knowledge" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                    Knowledge
                  </Link>
                  <Link to="/sources" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                    Sources
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/sessions/:id" element={<SessionDetailPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/sources" element={<SourcesPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              🏔️ SHERPA V1 - Autonomous Coding Orchestrator
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
