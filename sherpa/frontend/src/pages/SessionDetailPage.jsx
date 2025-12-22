import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Play, Pause, Square, CheckCircle } from 'lucide-react'
import api from '../lib/api'

function SessionDetailPage() {
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [features, setFeatures] = useState([])
  const [logs, setLogs] = useState([])
  const [commits, setCommits] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSessionDetails()

    // Setup SSE for real-time updates
    const eventSource = new EventSource(`http://localhost:8000/api/sessions/${id}/progress`)

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setSession(prev => ({ ...prev, ...data }))
    }

    return () => {
      eventSource.close()
    }
  }, [id])

  const fetchSessionDetails = async () => {
    try {
      const [sessionRes, logsRes, commitsRes] = await Promise.all([
        api.get(`/api/sessions/${id}`),
        api.get(`/api/sessions/${id}/logs`),
        api.get(`/api/sessions/${id}/commits`)
      ])

      setSession(sessionRes.data)
      setFeatures(sessionRes.data.features || [])
      setLogs(logsRes.data)
      setCommits(commitsRes.data)
    } catch (error) {
      console.error('Error fetching session details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    try {
      await api.post(`/api/sessions/${id}/stop`)
      fetchSessionDetails()
    } catch (error) {
      console.error('Error stopping session:', error)
    }
  }

  const handlePause = async () => {
    try {
      await api.post(`/api/sessions/${id}/pause`)
      fetchSessionDetails()
    } catch (error) {
      console.error('Error pausing session:', error)
    }
  }

  const handleResume = async () => {
    try {
      await api.post(`/api/sessions/${id}/resume`)
      fetchSessionDetails()
    } catch (error) {
      console.error('Error resuming session:', error)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading session...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{session?.name || `Session ${id}`}</h1>
          <p className="mt-2 text-gray-600">Started {new Date(session?.created_at).toLocaleString()}</p>
        </div>
        <div className="flex gap-2">
          {session?.status === 'active' && (
            <>
              <button onClick={handlePause} className="btn-secondary flex items-center gap-2">
                <Pause className="h-4 w-4" />
                Pause
              </button>
              <button onClick={handleStop} className="btn-secondary flex items-center gap-2">
                <Square className="h-4 w-4" />
                Stop
              </button>
            </>
          )}
          {session?.status === 'paused' && (
            <button onClick={handleResume} className="btn-primary flex items-center gap-2">
              <Play className="h-4 w-4" />
              Resume
            </button>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Progress</h2>
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Overall Progress</span>
            <span className="font-medium">{session?.progress || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-primary-600 h-3 rounded-full transition-all"
              style={{ width: `${session?.progress || 0}%` }}
            ></div>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          {session?.completed_features || 0} / {session?.total_features || 0} features completed
        </p>
      </div>

      {/* Feature List */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Features</h2>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {features.map((feature, index) => (
            <div key={index} className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded">
              <CheckCircle className={`h-5 w-5 mt-0.5 ${feature.passes ? 'text-green-500' : 'text-gray-300'}`} />
              <div className="flex-1">
                <p className={`text-sm ${feature.passes ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Logs */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Live Logs</h2>
        <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto font-mono text-sm">
          {logs.map((log, index) => (
            <div key={index} className={`${
              log.level === 'ERROR' ? 'text-red-400' :
              log.level === 'WARNING' ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
            </div>
          ))}
        </div>
      </div>

      {/* Git Commits */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Git Commits</h2>
        <div className="space-y-3">
          {commits.map((commit, index) => (
            <div key={index} className="border-l-2 border-primary-600 pl-4 py-2">
              <p className="font-mono text-sm text-gray-600">{commit.hash}</p>
              <p className="text-sm mt-1">{commit.message}</p>
              <p className="text-xs text-gray-500 mt-1">{new Date(commit.timestamp).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SessionDetailPage
