import { useState, useEffect } from 'react'
import { Loader, AlertCircle, RefreshCw, FileText, User, Calendar } from 'lucide-react'
import api from '../lib/api'

function WorkItemsList() {
  const [workItems, setWorkItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [topCount, setTopCount] = useState(100)

  useEffect(() => {
    fetchWorkItems()
  }, [])

  const fetchWorkItems = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (query.trim()) {
        params.append('query', query)
      }
      params.append('top', topCount)

      const response = await api.get(`/api/azure-devops/work-items?${params.toString()}`)

      if (response.data.success) {
        setWorkItems(response.data.work_items || [])
      } else {
        setError('Failed to fetch work items')
      }
    } catch (error) {
      console.error('Error fetching work items:', error)
      if (error.response?.status === 401) {
        setError('Azure DevOps not configured. Please connect to Azure DevOps first.')
      } else {
        setError(error.response?.data?.detail || 'Failed to fetch work items')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    fetchWorkItems()
  }

  const getStateColor = (state) => {
    const stateColors = {
      'New': 'bg-blue-100 text-blue-800',
      'Active': 'bg-yellow-100 text-yellow-800',
      'Resolved': 'bg-green-100 text-green-800',
      'Closed': 'bg-gray-100 text-gray-800',
      'Removed': 'bg-red-100 text-red-800'
    }
    return stateColors[state] || 'bg-gray-100 text-gray-800'
  }

  const getTypeColor = (type) => {
    const typeColors = {
      'User Story': 'bg-purple-100 text-purple-800',
      'Bug': 'bg-red-100 text-red-800',
      'Task': 'bg-blue-100 text-blue-800',
      'Feature': 'bg-indigo-100 text-indigo-800',
      'Epic': 'bg-pink-100 text-pink-800'
    }
    return typeColors[type] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    } catch {
      return 'Invalid Date'
    }
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Work Items</h2>
          <p className="text-sm text-gray-600 mt-1">
            {workItems.length > 0 ? `${workItems.length} work items found` : 'No work items'}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="btn-secondary inline-flex items-center"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Query Input (Optional) */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Custom WIQL Query (Optional)
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.TeamProject] = @project"
          className="input-field font-mono text-sm"
          rows={3}
        />
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center space-x-4">
            <label className="text-sm text-gray-700">
              Top:
              <input
                type="number"
                value={topCount}
                onChange={(e) => setTopCount(parseInt(e.target.value) || 100)}
                min="1"
                max="200"
                className="ml-2 w-20 px-2 py-1 border border-gray-300 rounded"
              />
            </label>
          </div>
          <button
            onClick={fetchWorkItems}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Fetching...' : 'Fetch Work Items'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="h-8 w-8 text-blue-600 animate-spin" />
          <span className="ml-3 text-gray-600">Fetching work items...</span>
        </div>
      )}

      {/* Work Items List */}
      {!loading && !error && workItems.length === 0 && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Work Items</h3>
          <p className="text-gray-600">
            No work items found. Connect to Azure DevOps and fetch work items.
          </p>
        </div>
      )}

      {!loading && !error && workItems.length > 0 && (
        <div className="space-y-3">
          {workItems.map((item) => (
            <div
              key={item.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-mono text-gray-500">#{item.id}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getTypeColor(item.type)}`}>
                      {item.type}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStateColor(item.state)}`}>
                      {item.state}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-gray-900 mb-2">
                    {item.title}
                  </h3>
                  {item.description && (
                    <div
                      className="text-sm text-gray-600 line-clamp-2"
                      dangerouslySetInnerHTML={{ __html: item.description }}
                    />
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-4 text-xs text-gray-500 mt-3 pt-3 border-t border-gray-100">
                {item.assigned_to && (
                  <div className="flex items-center">
                    <User className="h-3.5 w-3.5 mr-1" />
                    <span>{item.assigned_to}</span>
                  </div>
                )}
                {item.changed_date && (
                  <div className="flex items-center">
                    <Calendar className="h-3.5 w-3.5 mr-1" />
                    <span>Updated: {formatDate(item.changed_date)}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {!loading && !error && workItems.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{workItems.length}</div>
              <div className="text-sm text-gray-600">Total Items</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">
                {workItems.filter(item => item.state === 'Active').length}
              </div>
              <div className="text-sm text-gray-600">Active</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {workItems.filter(item => item.state === 'New').length}
              </div>
              <div className="text-sm text-gray-600">New</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {workItems.filter(item => item.state === 'Resolved' || item.state === 'Closed').length}
              </div>
              <div className="text-sm text-gray-600">Resolved</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorkItemsList
