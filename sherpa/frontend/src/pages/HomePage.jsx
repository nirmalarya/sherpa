import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, FileText, Activity, Clock, CheckCircle, XCircle, StopCircle, PauseCircle } from 'lucide-react'
import NewSessionModal from '../components/NewSessionModal'
import GenerateFilesModal from '../components/GenerateFilesModal'
import ErrorMessage from '../components/ErrorMessage'
import { formatRelativeTime, formatAbsoluteTime } from '../lib/timeUtils'

function HomePage() {
  const [sessions, setSessions] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [activityLoading, setActivityLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activityError, setActivityError] = useState(null)
  const [showNewSessionModal, setShowNewSessionModal] = useState(false)
  const [showGenerateFilesModal, setShowGenerateFilesModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchActiveSessions()
    fetchRecentActivity()

    // Auto-refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      fetchActiveSessions()
      fetchRecentActivity()
    }, 30000)

    // Cleanup interval on unmount
    return () => clearInterval(refreshInterval)
  }, [])

  const fetchActiveSessions = async () => {
    try {
      setError(null) // Clear any previous errors
      const response = await fetch('http://localhost:8001/api/sessions?status=active')

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
      setError({
        message: 'Unable to load active sessions. Please check your connection and try again.',
        technicalDetails: `${error.message}\n\nEndpoint: GET /api/sessions?status=active\nTimestamp: ${new Date().toISOString()}`
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentActivity = async () => {
    try {
      setActivityError(null)
      const response = await fetch('http://localhost:8001/api/activity?limit=10')

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setActivity(data.events || [])
    } catch (error) {
      console.error('Error fetching activity:', error)
      setActivityError({
        message: 'Unable to load recent activity.',
        technicalDetails: `${error.message}\n\nEndpoint: GET /api/activity\nTimestamp: ${new Date().toISOString()}`
      })
    } finally {
      setActivityLoading(false)
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
      <section aria-labelledby="quick-actions-heading" className="mb-8">
        <h2 id="quick-actions-heading" className="sr-only">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            data-action="new-session"
            onClick={() => setShowNewSessionModal(true)}
            className="card flex items-center p-6 hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2"
            aria-label="Start a new autonomous coding session"
          >
            <Plus className="h-8 w-8 text-primary-600" aria-hidden="true" />
            <div className="ml-4 text-left">
              <h3 className="text-lg font-semibold">New Session</h3>
              <p className="text-sm text-gray-600">Start autonomous coding session</p>
            </div>
          </button>

          <button
            data-action="generate-files"
            onClick={() => setShowGenerateFilesModal(true)}
            className="card flex items-center p-6 hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2"
            aria-label="Generate instruction files for agents"
          >
            <FileText className="h-8 w-8 text-primary-600" aria-hidden="true" />
            <div className="ml-4 text-left">
              <h3 className="text-lg font-semibold">Generate Files</h3>
              <p className="text-sm text-gray-600">Create instruction files for agents</p>
            </div>
          </button>
        </div>
      </section>

      {/* Active Sessions */}
      <section aria-labelledby="active-sessions-heading" className="mb-8">
        <h2 id="active-sessions-heading" className="text-2xl font-bold text-gray-900 mb-4">Active Sessions</h2>

        {/* Error Message */}
        {error && (
          <ErrorMessage
            message={error.message}
            technicalDetails={error.technicalDetails}
            onDismiss={() => setError(null)}
            onRetry={fetchActiveSessions}
            className="mb-4"
          />
        )}

        {loading ? (
          <div className="text-center py-12" role="status" aria-live="polite">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" aria-hidden="true"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        ) : sessions.length === 0 && !error ? (
          <div className="card text-center py-12" role="status">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" aria-hidden="true" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No active sessions</h3>
            <p className="text-gray-600">Start a new session to begin coding</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" role="list" aria-label="Active sessions">
            {sessions.map((session) => {
              const progress = session.total_features > 0
                ? Math.round((session.completed_features / session.total_features) * 100)
                : 0
              const sessionName = session.spec_file || session.id

              // Helper function to get status badge color
              const getStatusColor = (status) => {
                switch (status) {
                  case 'active':
                    return 'bg-blue-100 text-blue-800'
                  case 'completed':
                    return 'bg-green-100 text-green-800'
                  case 'error':
                    return 'bg-red-100 text-red-800'
                  case 'paused':
                    return 'bg-yellow-100 text-yellow-800'
                  case 'stopped':
                    return 'bg-orange-100 text-orange-800'
                  default:
                    return 'bg-gray-100 text-gray-800'
                }
              }

              return (
                <Link
                  key={session.id}
                  to={`/sessions/${session.id}`}
                  className="card hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2"
                  role="listitem"
                  aria-label={`Session ${sessionName}, ${progress}% complete, ${session.status} status`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg">{sessionName}</h3>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${getStatusColor(session.status)}`} aria-label={`Status: ${session.status || 'active'}`}>
                      {session.status || 'active'}
                    </span>
                  </div>
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium" aria-label={`${progress} percent complete`}>{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2" role="progressbar" aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100" aria-label="Session progress">
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
      </section>

      {/* Recent Activity */}
      <section aria-labelledby="recent-activity-heading">
        <h2 id="recent-activity-heading" className="text-2xl font-bold text-gray-900 mb-4">Recent Activity</h2>

        {/* Activity Error Message */}
        {activityError && (
          <ErrorMessage
            message={activityError.message}
            technicalDetails={activityError.technicalDetails}
            onDismiss={() => setActivityError(null)}
            onRetry={fetchRecentActivity}
            className="mb-4"
          />
        )}

        {activityLoading ? (
          <div className="card text-center py-8" role="status" aria-live="polite">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" aria-hidden="true"></div>
            <p className="mt-3 text-gray-600 text-sm">Loading activity...</p>
          </div>
        ) : activity.length === 0 && !activityError ? (
          <div className="card text-center py-8" role="status">
            <Activity className="h-10 w-10 text-gray-400 mx-auto mb-3" aria-hidden="true" />
            <p className="text-gray-600">No recent activity</p>
          </div>
        ) : (
          <div className="card">
            <ul className="space-y-3" role="list" aria-label="Recent activity events">
              {activity.map((event) => {
                // Helper function to get icon for event type
                const getEventIcon = (type) => {
                  switch (type) {
                    case 'session_completed':
                      return <CheckCircle className="h-5 w-5 text-green-600" aria-label="Completed" />
                    case 'session_error':
                      return <XCircle className="h-5 w-5 text-red-600" aria-label="Error" />
                    case 'session_stopped':
                      return <StopCircle className="h-5 w-5 text-orange-600" aria-label="Stopped" />
                    case 'session_paused':
                      return <PauseCircle className="h-5 w-5 text-yellow-600" aria-label="Paused" />
                    case 'session_started':
                      return <Activity className="h-5 w-5 text-blue-600" aria-label="Started" />
                    default:
                      return <Clock className="h-5 w-5 text-gray-600" aria-label="Event" />
                  }
                }

                return (
                  <li key={event.id}>
                    <Link
                      to={`/sessions/${event.session_id}`}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2"
                      aria-label={`${event.message}, ${formatRelativeTime(event.timestamp)}`}
                    >
                      <div className="flex-shrink-0 mt-0.5" aria-hidden="true">
                        {getEventIcon(event.type)}
                      </div>
                      <div className="flex-grow min-w-0">
                        <p className="text-sm text-gray-900 font-medium">{event.message}</p>
                        <time
                          className="text-xs text-gray-500 mt-0.5 cursor-help"
                          dateTime={event.timestamp}
                          title={formatAbsoluteTime(event.timestamp)}
                        >
                          {formatRelativeTime(event.timestamp)}
                        </time>
                      </div>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        )}
      </section>

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
