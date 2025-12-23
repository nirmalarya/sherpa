import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Play, Pause, Square, CheckCircle } from 'lucide-react'
import api from '../lib/api'
import SessionMonitor from '../components/SessionMonitor'
import ProgressChart from '../components/ProgressChart'
import ConfirmDialog from '../components/ConfirmDialog'
import Breadcrumb from '../components/Breadcrumb'

function SessionDetailPage() {
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [features, setFeatures] = useState([])
  const [logs, setLogs] = useState([])
  const [commits, setCommits] = useState([])
  const [loading, setLoading] = useState(true)
  const [progressData, setProgressData] = useState([])
  const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, action: null, title: '', message: '' })

  useEffect(() => {
    fetchSessionDetails()
  }, [id])

  // Auto-refresh logs and commits every 30 seconds
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      // Only refresh logs and commits, not full session details
      // Session details are updated via SessionMonitor SSE
      fetchLogsAndCommits()
    }, 30000)

    return () => clearInterval(refreshInterval)
  }, [id])

  const fetchLogsAndCommits = async () => {
    try {
      const [logsRes, commitsRes] = await Promise.all([
        api.get(`/api/sessions/${id}/logs`),
        api.get(`/api/sessions/${id}/commits`)
      ])
      setLogs(logsRes.data.logs || [])
      setCommits(commitsRes.data.commits || [])
    } catch (error) {
      console.error('Error refreshing logs and commits:', error)
    }
  }

  // Handle progress updates from SessionMonitor
  const handleProgressUpdate = (data) => {
    setSession(prev => ({ ...prev, ...data }))

    // Add new data point to progress chart
    if (data.completed_features !== undefined && data.total_features !== undefined) {
      const newDataPoint = {
        timestamp: new Date().toLocaleTimeString(),
        completionPercent: data.total_features > 0
          ? Math.round((data.completed_features / data.total_features) * 100)
          : 0,
        completed: data.completed_features,
        total: data.total_features
      }
      setProgressData(prev => [...prev, newDataPoint])
    }
  }

  const handleSessionComplete = (data) => {
    console.log('Session completed:', data)
    fetchSessionDetails() // Refresh all data when session completes
  }

  const handleMonitorError = (error) => {
    console.error('SessionMonitor error:', error)
  }

  const fetchSessionDetails = async () => {
    try {
      const [sessionRes, logsRes, commitsRes] = await Promise.all([
        api.get(`/api/sessions/${id}`),
        api.get(`/api/sessions/${id}/logs`),
        api.get(`/api/sessions/${id}/commits`)
      ])

      setSession(sessionRes.data)
      setFeatures(sessionRes.data.features || [])
      setLogs(logsRes.data.logs || [])
      setCommits(commitsRes.data.commits || [])

      // Initialize progress data with current state
      const currentProgress = {
        timestamp: new Date().toLocaleTimeString(),
        completionPercent: sessionRes.data.total_features > 0
          ? Math.round((sessionRes.data.completed_features / sessionRes.data.total_features) * 100)
          : 0,
        completed: sessionRes.data.completed_features || 0,
        total: sessionRes.data.total_features || 0
      }
      setProgressData([currentProgress])
    } catch (error) {
      console.error('Error fetching session details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStopClick = () => {
    setConfirmDialog({
      isOpen: true,
      action: 'stop',
      title: 'Stop Session',
      message: 'Are you sure you want to stop this session? This will terminate the coding process and cannot be resumed.'
    })
  }

  const handlePauseClick = () => {
    setConfirmDialog({
      isOpen: true,
      action: 'pause',
      title: 'Pause Session',
      message: 'Are you sure you want to pause this session? You can resume it later from where it left off.'
    })
  }

  const handleConfirmAction = async () => {
    const action = confirmDialog.action
    try {
      if (action === 'stop') {
        await api.post(`/api/sessions/${id}/stop`)
      } else if (action === 'pause') {
        await api.post(`/api/sessions/${id}/pause`)
      }
      fetchSessionDetails()
    } catch (error) {
      console.error(`Error ${action}ing session:`, error)
    }
  }

  const handleCancelDialog = () => {
    setConfirmDialog({ isOpen: false, action: null, title: '', message: '' })
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
      {/* Breadcrumb Navigation */}
      <Breadcrumb
        items={[
          { label: 'Home', path: '/' },
          { label: 'Sessions', path: '/sessions' },
          { label: session?.spec_file || `Session ${id}` }
        ]}
      />

      {/* Header */}
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{session?.spec_file || `Session ${id}`}</h1>
          <p className="mt-2 text-gray-600">Started {session?.started_at ? new Date(session.started_at).toLocaleString() : 'N/A'}</p>
        </div>
        <div className="flex gap-2">
          {session?.status === 'active' && (
            <>
              <button onClick={handlePauseClick} className="btn-secondary flex items-center gap-2">
                <Pause className="h-4 w-4" />
                Pause
              </button>
              <button onClick={handleStopClick} className="btn-secondary flex items-center gap-2">
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

      {/* Session Monitor - SSE Connection */}
      <SessionMonitor
        sessionId={id}
        onProgress={handleProgressUpdate}
        onComplete={handleSessionComplete}
        onError={handleMonitorError}
      />

      {/* Progress */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Progress</h2>
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Overall Progress</span>
            <span className="font-medium">
              {session?.total_features > 0
                ? Math.round((session.completed_features / session.total_features) * 100)
                : 0}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-primary-600 h-3 rounded-full transition-all"
              style={{
                width: `${session?.total_features > 0
                  ? Math.round((session.completed_features / session.total_features) * 100)
                  : 0}%`
              }}
            ></div>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          {session?.completed_features || 0} / {session?.total_features || 0} features completed
        </p>

        {/* Progress Chart */}
        <div className="mt-6">
          <h3 className="text-lg font-medium mb-3">Progress Over Time</h3>
          <ProgressChart data={progressData} height={250} />
        </div>
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

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        onClose={handleCancelDialog}
        onConfirm={handleConfirmAction}
        title={confirmDialog.title}
        message={confirmDialog.message}
        confirmText={confirmDialog.action === 'stop' ? 'Stop Session' : 'Pause Session'}
        confirmButtonClass={confirmDialog.action === 'stop' ? 'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg' : 'btn-primary'}
      />
    </div>
  )
}

export default SessionDetailPage
