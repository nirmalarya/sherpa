import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader } from 'lucide-react'
import api from '../lib/api'

function SourcesPage() {
  const [azureConfig, setAzureConfig] = useState({
    organization: '',
    project: '',
    pat: ''
  })
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [testing, setTesting] = useState(false)
  const [syncStatus, setSyncStatus] = useState(null)

  useEffect(() => {
    fetchSyncStatus()
  }, [])

  const fetchSyncStatus = async () => {
    try {
      const response = await api.get('/api/azure-devops/status')
      setSyncStatus(response.data)
    } catch (error) {
      console.error('Error fetching sync status:', error)
    }
  }

  const handleTestConnection = async () => {
    setTesting(true)
    setConnectionStatus(null)

    try {
      await api.post('/api/azure-devops/connect', azureConfig)
      setConnectionStatus({ success: true, message: 'Connection successful!' })
      fetchSyncStatus()
    } catch (error) {
      setConnectionStatus({
        success: false,
        message: error.response?.data?.message || 'Connection failed'
      })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    try {
      await api.post('/api/azure-devops/save-config', azureConfig)
      alert('Configuration saved successfully!')
    } catch (error) {
      console.error('Error saving configuration:', error)
      alert('Failed to save configuration')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Sources</h1>
        <p className="mt-2 text-gray-600">Configure external sources for specs and work items</p>
      </div>

      {/* Azure DevOps Configuration */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Azure DevOps</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Organization URL
            </label>
            <input
              type="text"
              placeholder="https://dev.azure.com/your-org"
              value={azureConfig.organization}
              onChange={(e) => setAzureConfig({ ...azureConfig, organization: e.target.value })}
              className="input w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Name
            </label>
            <input
              type="text"
              placeholder="YourProject"
              value={azureConfig.project}
              onChange={(e) => setAzureConfig({ ...azureConfig, project: e.target.value })}
              className="input w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Personal Access Token (PAT)
            </label>
            <input
              type="password"
              placeholder="Enter your PAT"
              value={azureConfig.pat}
              onChange={(e) => setAzureConfig({ ...azureConfig, pat: e.target.value })}
              className="input w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Requires: Work Items (Read, Write), Code (Read)
            </p>
          </div>

          {connectionStatus && (
            <div className={`p-4 rounded-lg flex items-center gap-2 ${
              connectionStatus.success
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}>
              {connectionStatus.success ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <XCircle className="h-5 w-5" />
              )}
              <span>{connectionStatus.message}</span>
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="btn-secondary flex items-center gap-2"
            >
              {testing ? (
                <Loader className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
              Test Connection
            </button>
            <button
              onClick={handleSave}
              className="btn-primary"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>

      {/* Sync Status */}
      {syncStatus && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Sync Status</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Last Sync:</span>
              <span className="font-medium">
                {syncStatus.last_sync ? new Date(syncStatus.last_sync).toLocaleString() : 'Never'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`font-medium ${
                syncStatus.status === 'success' ? 'text-green-600' : 'text-red-600'
              }`}>
                {syncStatus.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Work Items Synced:</span>
              <span className="font-medium">{syncStatus.work_items_count || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* File Source Configuration */}
      <div className="card mt-6">
        <h2 className="text-xl font-semibold mb-4">File Sources</h2>
        <p className="text-gray-600 mb-4">
          Configure local file paths for spec files
        </p>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Spec Directory
          </label>
          <input
            type="text"
            placeholder="./specs"
            className="input w-full"
          />
        </div>
        <button className="btn-primary mt-4">
          Add Directory
        </button>
      </div>
    </div>
  )
}

export default SourcesPage
