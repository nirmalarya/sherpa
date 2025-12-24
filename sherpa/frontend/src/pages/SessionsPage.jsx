import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, FolderOpen, Plus } from 'lucide-react'
import api from '../lib/api'
import ErrorMessage from '../components/ErrorMessage'
import Breadcrumb from '../components/Breadcrumb'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { formatRelativeTime, formatAbsoluteTime } from '../lib/timeUtils'

function SessionsPage() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date') // 'date', 'status', 'progress'
  const [sortDirection, setSortDirection] = useState('desc') // 'asc' or 'desc'
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10) // Sessions per page

  useEffect(() => {
    fetchSessions()

    // Auto-refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      fetchSessions()
    }, 30000)

    // Cleanup interval on unmount
    return () => clearInterval(refreshInterval)
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

  const handleSort = (column) => {
    if (sortBy === column) {
      // Toggle direction if clicking same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      // Set new column and default to descending
      setSortBy(column)
      setSortDirection('desc')
    }
  }

  const filteredSessions = sessions.filter(session => {
    const sessionName = session.spec_file || session.id || ''
    return sessionName.toLowerCase().includes(search.toLowerCase())
  })

  // Sort the filtered sessions
  const sortedSessions = [...filteredSessions].sort((a, b) => {
    let comparison = 0

    if (sortBy === 'date') {
      const dateA = new Date(a.started_at || 0)
      const dateB = new Date(b.started_at || 0)
      comparison = dateA - dateB
    } else if (sortBy === 'status') {
      const statusA = a.status || ''
      const statusB = b.status || ''
      comparison = statusA.localeCompare(statusB)
    } else if (sortBy === 'progress') {
      const progressA = a.total_features > 0 ? (a.completed_features / a.total_features) : 0
      const progressB = b.total_features > 0 ? (b.completed_features / b.total_features) : 0
      comparison = progressA - progressB
    }

    return sortDirection === 'asc' ? comparison : -comparison
  })

  // Pagination calculations
  const totalPages = Math.ceil(sortedSessions.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedSessions = sortedSessions.slice(startIndex, endIndex)

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [search, statusFilter, sortBy, sortDirection])

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
      // Scroll to top of page when changing pages
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const getPageNumbers = () => {
    const pages = []
    const maxVisiblePages = 5

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Show first, last, current and nearby pages
      if (currentPage <= 3) {
        // Near beginning
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        // Near end
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        // Middle
        pages.push(1)
        pages.push('...')
        pages.push(currentPage - 1)
        pages.push(currentPage)
        pages.push(currentPage + 1)
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumb
        items={[
          { label: 'Home', path: '/' },
          { label: 'Sessions' }
        ]}
      />

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
          <LoadingSkeleton variant="table" count={5} />
        ) : filteredSessions.length === 0 && !error ? (
          <div className="text-center py-16 px-4">
            {/* Empty State Icon */}
            <div className="flex justify-center mb-6">
              <div className="rounded-full bg-gray-100 p-6">
                <FolderOpen className="h-16 w-16 text-gray-400" />
              </div>
            </div>

            {/* Empty State Message */}
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {sessions.length === 0 ? 'No sessions yet' : 'No sessions found'}
            </h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              {sessions.length === 0
                ? 'Start your first autonomous coding session to see it appear here.'
                : 'Try adjusting your search or filter criteria to find what you\'re looking for.'}
            </p>

            {/* Call to Action - only show if there are truly no sessions */}
            {sessions.length === 0 && (
              <Link
                to="/"
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-5 w-5" />
                Create Your First Session
              </Link>
            )}
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Session
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('status')}
                  aria-label="Sort by status"
                >
                  <div className="flex items-center gap-1">
                    <span>Status</span>
                    {sortBy === 'status' && (
                      sortDirection === 'asc' ?
                        <ArrowUp className="h-4 w-4" aria-label="Sorted ascending" /> :
                        <ArrowDown className="h-4 w-4" aria-label="Sorted descending" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('progress')}
                  aria-label="Sort by progress"
                >
                  <div className="flex items-center gap-1">
                    <span>Progress</span>
                    {sortBy === 'progress' && (
                      sortDirection === 'asc' ?
                        <ArrowUp className="h-4 w-4" aria-label="Sorted ascending" /> :
                        <ArrowDown className="h-4 w-4" aria-label="Sorted descending" />
                    )}
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('date')}
                  aria-label="Sort by date"
                >
                  <div className="flex items-center gap-1">
                    <span>Started</span>
                    {sortBy === 'date' && (
                      sortDirection === 'asc' ?
                        <ArrowUp className="h-4 w-4" aria-label="Sorted ascending" /> :
                        <ArrowDown className="h-4 w-4" aria-label="Sorted descending" />
                    )}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedSessions.map((session) => {
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
                      <span
                        title={formatAbsoluteTime(session.started_at)}
                        className="cursor-help"
                      >
                        {formatRelativeTime(session.started_at)}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}

        {/* Pagination Controls */}
        {!loading && sortedSessions.length > itemsPerPage && (
          <div className="px-6 py-4 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-4">
            {/* Results info */}
            <div className="text-sm text-gray-600">
              Showing {startIndex + 1} to {Math.min(endIndex, sortedSessions.length)} of {sortedSessions.length} sessions
            </div>

            {/* Pagination buttons */}
            <div className="flex items-center gap-2">
              {/* Previous button */}
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`p-2 rounded border ${
                  currentPage === 1
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                aria-label="Previous page"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>

              {/* Page numbers */}
              <div className="flex items-center gap-1">
                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <span key={`ellipsis-${index}`} className="px-3 py-2 text-gray-500">
                      ...
                    </span>
                  ) : (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-3 py-2 rounded border ${
                        currentPage === page
                          ? 'bg-primary-600 text-white border-primary-600'
                          : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                      aria-label={`Go to page ${page}`}
                      aria-current={currentPage === page ? 'page' : undefined}
                    >
                      {page}
                    </button>
                  )
                ))}
              </div>

              {/* Next button */}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`p-2 rounded border ${
                  currentPage === totalPages
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                aria-label="Next page"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SessionsPage
