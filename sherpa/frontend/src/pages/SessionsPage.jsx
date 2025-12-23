import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter } from 'lucide-react'
import api from '../lib/api'
import ErrorMessage from '../components/ErrorMessage'

function SessionsPage() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    fetchSessions()
  }, [statusFilter])

  const fetchSessions = async () => {
    try {
      setError(null) // Clear any previous errors
      const params = statusFilter !== 'all' ? { status: statusFilter } : {}
      const response = await api.get('/api/sessions', { params })
      // API returns { sessions: [...], total: N, timestamp: "..." }
      setSessions(response.data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
      setError({
        message: 'Unable to load sessions. Please check your connection and try again.',
        technicalDetails: `${error.message}\n\nEndpoint: GET /api/sessions\nFilter: ${statusFilter}\nTimestamp: ${new Date().toISOString()}`
      })
    } finally {
      setLoading(false)
    }
  }

  const filteredSessions = sessions.filter(session => {
    const sessionName = session.spec_file || session.id || ''
    return sessionName.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Sessions</h1>
        <p className="mt-2 text-gray-600">View and manage all coding sessions</p>
      </div>

      {/* Filters */}
      <div className="card mb-6 flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search sessions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input w-full pl-10"
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="stopped">Stopped</option>
            <option value="paused">Paused</option>
            <option value="complete">Complete</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <ErrorMessage
          message={error.message}
          technicalDetails={error.technicalDetails}
          onDismiss={() => setError(null)}
          onRetry={fetchSessions}
          className="mb-6"
        />
      )}

      {/* Sessions Table */}
      <div className="card overflow-x-auto">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        ) : filteredSessions.length === 0 && !error ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No sessions found</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Session
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Started
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredSessions.map((session) => {
                const progress = session.total_features > 0
                  ? Math.round((session.completed_features / session.total_features) * 100)
                  : 0
                const sessionName = session.spec_file || session.id

                return (
                  <tr key={session.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-6 py-4">
                      <Link to={`/sessions/${session.id}`} className="text-primary-600 hover:text-primary-700 font-medium">
                        {sessionName}
                      </Link>
                      <div className="text-xs text-gray-500 mt-1">
                        {session.completed_features} / {session.total_features} features
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        session.status === 'active' ? 'bg-green-100 text-green-800' :
                        session.status === 'complete' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className="text-sm font-medium mr-2">{progress}%</span>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${progress}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {session.created_at ? new Date(session.created_at).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default SessionsPage
