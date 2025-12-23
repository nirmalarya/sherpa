import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, FileText, Activity } from 'lucide-react'
import NewSessionModal from '../components/NewSessionModal'
import GenerateFilesModal from '../components/GenerateFilesModal'

function HomePage() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showNewSessionModal, setShowNewSessionModal] = useState(false)
  const [showGenerateFilesModal, setShowGenerateFilesModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchActiveSessions()
  }, [])

  const fetchActiveSessions = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/sessions?status=active')
      const data = await response.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNewSessionSuccess = (session) => {
    // Navigate to the new session's detail page
    navigate(`/sessions/${session.id}`)
  }

  const handleGenerateFilesSuccess = (result) => {
    // Show success message or refresh page
    console.log('Files generated:', result)
    // Could show a toast notification here
    alert('Files generated successfully!')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Monitor your autonomous coding sessions</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <button
          onClick={() => setShowNewSessionModal(true)}
          className="card flex items-center p-6 hover:shadow-md transition-shadow"
        >
          <Plus className="h-8 w-8 text-primary-600" aria-label="New session icon" />
          <div className="ml-4 text-left">
            <h3 className="text-lg font-semibold">New Session</h3>
            <p className="text-sm text-gray-600">Start autonomous coding session</p>
          </div>
        </button>

        <button
          onClick={() => setShowGenerateFilesModal(true)}
          className="card flex items-center p-6 hover:shadow-md transition-shadow"
        >
          <FileText className="h-8 w-8 text-primary-600" aria-label="Generate files icon" />
          <div className="ml-4 text-left">
            <h3 className="text-lg font-semibold">Generate Files</h3>
            <p className="text-sm text-gray-600">Create instruction files for agents</p>
          </div>
        </button>
      </div>

      {/* Active Sessions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Active Sessions</h2>
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="card text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No active sessions</h3>
            <p className="text-gray-600">Start a new session to begin coding</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => {
              const progress = session.total_features > 0
                ? Math.round((session.completed_features / session.total_features) * 100)
                : 0
              const sessionName = session.spec_file || session.id

              return (
                <Link key={session.id} to={`/sessions/${session.id}`} className="card hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-lg mb-2">{sessionName}</h3>
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    {session.completed_features} / {session.total_features} features
                  </p>
                </Link>
              )
            })}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Activity</h2>
        <div className="card">
          <p className="text-gray-600">Activity feed will appear here</p>
        </div>
      </div>

      {/* Modals */}
      <NewSessionModal
        isOpen={showNewSessionModal}
        onClose={() => setShowNewSessionModal(false)}
        onSuccess={handleNewSessionSuccess}
      />
      <GenerateFilesModal
        isOpen={showGenerateFilesModal}
        onClose={() => setShowGenerateFilesModal(false)}
        onSuccess={handleGenerateFilesSuccess}
      />
    </div>
  )
}

export default HomePage
