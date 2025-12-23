import { useState, useEffect, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Mountain } from 'lucide-react'

// Lazy load pages for code splitting
const HomePage = lazy(() => import('./pages/HomePage'))
const SessionsPage = lazy(() => import('./pages/SessionsPage'))
const SessionDetailPage = lazy(() => import('./pages/SessionDetailPage'))
const KnowledgePage = lazy(() => import('./pages/KnowledgePage'))
const SourcesPage = lazy(() => import('./pages/SourcesPage'))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
const ErrorTestPage = lazy(() => import('./pages/ErrorTestPage'))

// Components - CommandPalette is not lazy loaded as it's used globally
import CommandPalette from './components/CommandPalette'

// Loading component for Suspense fallback
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
      <p className="mt-4 text-gray-600">Loading...</p>
    </div>
  </div>
)

function App() {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)

  // Global keyboard shortcut: Ctrl+K or Cmd+K to open command palette
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Check for Ctrl+K (Windows/Linux) or Cmd+K (Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <BrowserRouter>
      {/* Command Palette - Global keyboard shortcuts */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />

      <div className="min-h-screen flex flex-col">
        {/* Skip to main content link for keyboard users */}
        <a href="#main-content" className="skip-to-main">
          Skip to main content
        </a>

        {/* Navigation */}
        <nav className="bg-white border-b border-gray-200 shadow-sm" role="navigation" aria-label="Main navigation">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link to="/" className="flex items-center" aria-label="SHERPA V1 home">
                  <Mountain className="h-8 w-8 text-primary-600" aria-hidden="true" />
                  <span className="ml-2 text-xl font-bold text-gray-900">SHERPA V1</span>
                </Link>
                <div className="ml-10 flex items-center space-x-4" role="list">
                  <Link to="/" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2" role="listitem" aria-label="Navigate to Home">
                    Home
                  </Link>
                  <Link to="/sessions" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2" role="listitem" aria-label="Navigate to Sessions">
                    Sessions
                  </Link>
                  <Link to="/knowledge" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2" role="listitem" aria-label="Navigate to Knowledge">
                    Knowledge
                  </Link>
                  <Link to="/sources" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2" role="listitem" aria-label="Navigate to Sources">
                    Sources
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main id="main-content" className="flex-1" role="main" aria-label="Main content">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:id" element={<SessionDetailPage />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
              <Route path="/sources" element={<SourcesPage />} />
              <Route path="/error-test" element={<ErrorTestPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto" role="contentinfo">
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
